# Tasks: Geocode Camera Locations with Caching

**Input**: Design documents from `/specs/001-geocode-camera-locations/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial structure setup and configuration

- [X] T001 Initialize dependencies in pyproject.toml including tqdm and geopy
- [X] T002 Configure pytest suite configuration in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be complete before any user story can be implemented

- [X] T003 Track geocoding_cache.csv directly in the Git repository
- [X] T004 Implement a thread-safe global rate limiter / throttler lock in scrape_cameras.py
- [X] T005 Implement a thread-safe file lock for writing/saving cache CSV files in scrape_cameras.py

---

## Phase 3: User Story 1 - Map-Ready Scraped Output (Priority: P1) 🎯 MVP

**Goal**: Fetch coordinates for camera locations using a thread pool with dynamic progress bars, and append Latitude and Longitude to the CSV output.

**Independent Test**: Verify that running the scraper fetches coordinates from the external API in multiple threads, showing progress, and outputs them in `mn_cameras.csv`.

### Tests for User Story 1
- [X] T006 [P] [US1] Write test verifying geopy response parsing in tests/test_geocoder.py
- [X] T007 [P] [US1] Write test verifying CSV headers are correctly written with Latitude and Longitude in tests/test_csv_output.py

### Implementation for User Story 1
- [X] T008 [US1] Implement geocoding service fetch logic using geopy in scrape_cameras.py
- [X] T009 [US1] Update CSV builder to map and append Latitude and Longitude coordinates in scrape_cameras.py
- [X] T010 [US1] Implement multi-threaded geocoding worker pool using ThreadPoolExecutor in scrape_cameras.py
- [X] T011 [US1] Integrate thread-safe global lock to enforce 1-second query throttle in scrape_cameras.py
- [X] T012 [US1] Add tqdm progress bar integration for geocoding stage in scrape_cameras.py
- [X] T013 [US1] Integrate parallel geocoding execution block into main flow in scrape_cameras.py

**Checkpoint**: User Story 1 is functional. Scraper fetches coordinates concurrently, throttles requests, updates the progress bar, and outputs to CSV.

---

## Phase 4: User Story 2 - Cached Geocoding for Performance (Priority: P2)

**Goal**: Cache coordinates in a separate `geocoding_cache.csv` file using the camera URI as a key to avoid redundant API queries, and track the cache file in Git.

**Independent Test**: Run the scraper twice. The second run completes in < 10 seconds and makes 0 geocoding API calls.

### Tests for User Story 2
- [X] T014 [P] [US2] Write unit tests verifying CSV cache read/write logic and cache hit/miss behavior in tests/test_cache.py

### Implementation for User Story 2
- [X] T015 [US2] Implement CSV cache loading at startup to read geocoding_cache.csv using pandas in scrape_cameras.py
- [X] T016 [US2] Update geocoding workflow to perform cache lookups by URI from geocoding_cache.csv before calling external geopy geocoding client in scrape_cameras.py
- [X] T017 [US2] Implement thread-safe periodic flushing of newly geocoded coordinates to geocoding_cache.csv every 50 records in scrape_cameras.py
- [X] T018 [US2] Implement final merge of cached coordinates from geocoding_cache.csv into fetched camera views before saving to mn_cameras.csv in scrape_cameras.py

**Checkpoint**: User Stories 1 and 2 work together. Coordinates are cached in a separate CSV file and committed, and subsequent runs read from the cache file instantly.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, validation, and documentation updates.

- [X] T019 Update README.md with geocoding setup, concurrency, and caching info
- [X] T020 Run the validation scenarios in specs/001-geocode-camera-locations/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup (Phase 1).
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2).
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3).
- **Polish (Phase 5)**: Depends on User Stories 1 and 2 completion.

### Parallel Opportunities

- T006 and T007 can run in parallel.
- Unit tests in T014 can be written in parallel with T012/T013.

---

## Parallel Example: User Story 1

```bash
# Launch test creation tasks in parallel
Task: "Write test verifying geopy response parsing in tests/test_geocoder.py"
Task: "Write test verifying CSV headers are correctly written with Latitude and Longitude in tests/test_csv_output.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Setup test suite.
2. Implement geocoder client and thread-safe lock rate limit query handler.
3. Update CSV output schema to include Latitude/Longitude.
4. Integrate tqdm progress bar and thread pool, then run scraper and verify coordinates are populated.

### Incremental Delivery
1. Implement loading/saving cache coordinates from/to `geocoding_cache.csv`.
2. Update scraper workflow to check loaded cache coordinates by URI before geocoding.
3. Implement periodic saving (every 50 geocoded items) with a thread-safe lock protecting cache writes.
4. Merge cache results with camera list to output the final `mn_cameras.csv` at the very end of execution.
5. Track `geocoding_cache.csv` in Git.
6. Verify subsequent run speed and cache hit rates.
