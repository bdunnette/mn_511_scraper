# Feature Specification: Geocode Camera Locations with Caching

**Feature Branch**: `001-geocode-camera-locations`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "geocode camera locations in output; cache geocoding results to improve performance"

## Clarifications

### Session 2026-07-10

- Q: How should the system handle rate limiting when executing geocoding across multiple parallel threads? → A: Use a global thread-safe rate limiter (lock/semaphore) to guarantee at least 1.0 second between external Nominatim calls across all threads.
- Q: How should the geocoding_cache.json file be handled in Git? → A: Remove geocoding_cache.json from .gitignore and track it directly in Git to share already resolved coordinates.
- Q: Should we add tqdm to the list of project dependencies? → A: Yes, add tqdm to pyproject.toml and use it in scrape_cameras.py for geocoding progress tracking.
- Q: How should the system identify matching cameras in the existing CSV file to determine if they already have location coordinates saved? → A: Match by unique URI identifier, loading the existing mn_cameras.csv using pandas, and skipping geocoding for cameras that already have locations saved in the CSV.
- Q: What strategy should be used to trigger saving/flushing the geocoding results to the CSV during execution? → A: Save the CSV periodically to disk after every 50 camera locations are successfully geocoded to allow resuming if interrupted.
- Q: What should the name of the separate geocoding cache CSV file be? → A: geocoding_cache.csv in the project root directory, which is periodically saved and loaded separately before merging with the main camera dataframe.
- Q: How should the custom User-Agent be passed when instantiating geopy's Nominatim geocoder? → A: Passed directly as user_agent in the geopy Nominatim constructor.
- Q: Should we switch to geopy async mode? → A: No, retain multi-threaded execution model with rate-limiting locks to comply with the 1 req/sec Nominatim policy.
- Q: Should we adopt MiniHuey for task scheduling and throttling? → A: No, stick to the simple thread pool and rate-limiting locks to avoid task queue dependency overhead.
- Q: Should cache matching rely strictly on URI even if camera titles change? → A: Yes, always check by unique URI and skip geocoding if it exists in the cache, ignoring text details.



## User Scenarios & Testing *(mandatory)*

### User Story 1 - Map-Ready Scraped Output (Priority: P1)

As a data analyst or map developer, I want scraped camera data to include latitude and longitude coordinates so that I can immediately plot the camera locations on a map without performing secondary geocoding.

**Why this priority**: Coordinates are the core value of this feature, transforming raw text descriptions into geographic coordinates that can be visualized.

**Independent Test**: Can be tested by running the scraper on a small set of cameras and verifying that the output contains non-empty, valid latitude and longitude fields.

**Acceptance Scenarios**:

1. **Given** the scraper executes successfully, **When** the output is generated, **Then** each camera entry contains "Latitude" and "Longitude" fields.
2. **Given** a camera location description, **When** geocoded, **Then** the coordinates match the physical roadway or intersection described in the camera title.

---

### User Story 2 - Cached Geocoding for Performance (Priority: P2)

As a system operator, I want geocoding results to be cached directly in a separate geocoding_cache.csv file so that subsequent scraper runs are fast, do not exceed external geocoding API rate limits, and output data is safely written in bulk at the end of execution.

**Why this priority**: Standard geocoding services have strict rate limits and network latency. Caching in a separate cache file protects external resources and prevents incomplete CSV output.

**Independent Test**: Can be tested by running the scraper twice. The second run should complete significantly faster and make zero external geocoding network calls for already known cameras.

**Acceptance Scenarios**:

1. **Given** a camera location has been geocoded and saved in geocoding_cache.csv in a previous run, **When** the scraper runs again, **Then** the coordinates are retrieved from the cache file instead of the external geocoding service.
2. **Given** a new camera is added to the source dataset, **When** the scraper runs, **Then** the new camera is geocoded externally and its coordinates are saved to geocoding_cache.csv.

---

### Edge Cases

- **Geocoding Failures**: If the geocoding service is unavailable or cannot resolve a description, the scraper must not crash. It should leave the latitude/longitude blank for that camera, log a warning, and continue.
- **Malformed Location Text**: If the camera's roadway or description text is empty or malformed, the system should skip geocoding for that camera and output blank coordinate values.
- **Cache Corruption**: If the output CSV file is corrupt or unreadable, the system should log a warning, discard the corrupt file, and proceed with a fresh geocoding run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST fetch geographical coordinates (latitude and longitude) for each camera using the `geopy` library to interface with Nominatim.
- **FR-002**: The system MUST check the separate `geocoding_cache.csv` dataset before querying the external geocoding service for coordinates.
- **FR-003**: The system MUST skip geocoding for any camera that already has Latitude and Longitude values saved in `geocoding_cache.csv`.
- **FR-004**: The system MUST include "Latitude" and "Longitude" columns in the persisted CSV output.
- **FR-005**: The system MUST match existing camera records by unique `URI` identifier when loading cached geocoding results.
- **FR-006**: The system MUST handle geocoding service rate limits or temporary network failures gracefully by retrying with exponential backoff before falling back to empty coordinate values.
- **FR-007**: The system MUST support parallel geocoding using multiple threads.
- **FR-008**: The system MUST enforce a thread-safe global rate limiter to ensure that the 1 request per second Nominatim policy is respected across all concurrent threads.
- **FR-009**: The system MUST track the cache `geocoding_cache.csv` directly in the Git repository to share resolved location data.
- **FR-010**: The system MUST utilize `tqdm` to display a dynamic progress bar for the geocoding stage in the command-line interface.
- **FR-011**: The system MUST periodically save the cached dataset to `geocoding_cache.csv` after every 50 camera locations are successfully geocoded to allow resuming if interrupted.
- **FR-012**: The system MUST merge the cache coordinates with the fetched camera views and output the final combined data to `mn_cameras.csv` using pandas at the end of the run.
- **FR-013**: The system MUST configure the geopy Nominatim client with a descriptive User-Agent constructor parameter and specify timeout parameters cleanly.

### Key Entities *(include if feature involves data)*

- **Geocoding Cache (geocoding_cache.csv)**: A separate persistent CSV file containing camera coordinates indexed by camera URI.
- **Scraper Output (mn_cameras.csv)**: The final merged CSV dataset containing camera metadata, Latitude, and Longitude columns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Output CSV contains valid numerical latitude (between -90 and 90) and longitude (between -180 and 180) values for at least 95% of successfully geocoded cameras.
- **SC-002**: Scraper runs where 100% of cameras are cached complete in under 10 seconds (excluding the initial GraphQL fetch).
- **SC-003**: The external geocoding service is queried exactly 0 times for camera locations that are already present in the cache.

## Assumptions

- Camera physical locations are static; once a camera is geocoded, its coordinates do not change.
- A free or open geocoding service (e.g., OpenStreetMap Nominatim or equivalent public API) is acceptable and will be queried within its usage guidelines.
- The camera title/roadway field contains sufficient geographical detail (e.g., roadway name and intersection/landmark) to resolve a coordinate within Minnesota.
