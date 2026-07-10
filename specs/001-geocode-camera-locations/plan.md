# Implementation Plan: Geocode Camera Locations with Caching

**Branch**: `001-geocode-camera-locations` | **Date**: 2026-07-10 | **Spec**: [spec.md](file:///C:/Users/dunn0172/Documents/GitHub/mn_511_scraper/specs/001-geocode-camera-locations/spec.md)

**Input**: Feature specification from `/specs/001-geocode-camera-locations/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

The goal of this feature is to resolve and append geographic coordinates (latitude and longitude) to the scraped camera listings in the output CSV file (`mn_cameras.csv`). To optimize performance and ensure resiliency, a separate cache CSV file (`geocoding_cache.csv`) acts as the geocoding database. Geocoding queries are executed using the `geopy` library interface to Nominatim. Existing locations are loaded at startup by unique `URI` to skip already geocoded cameras. Cache results are periodically written back to the separate cache CSV (every 50 geocodes) to support resumption, and merged into the main camera dataframe at the end of the run.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: `requests` (for GraphQL fetch), `geopy` (for Nominatim queries), `pandas` (for parsing, filtering, merging, and flushing CSV data), `tqdm` (for geocoding progress bar visualization)

**Storage**: Separate local CSV file (`geocoding_cache.csv`) for cache; final local CSV file (`mn_cameras.csv`) for merged output.

**Testing**: `pytest` for unit/integration testing of geocoding wrapper, rate limiting, thread safety, cache retrieval, periodic saving, and merging logic.

**Target Platform**: Desktop / Command-Line Interface (CLI)

**Project Type**: CLI scraper/data utility script

**Performance Goals**: Cached runs must bypass external API queries and complete in under 10 seconds. Geocoding processing leverages threading to perform cache checks and concurrent lookups efficiently.

**Constraints**: Adhere strictly to the OpenStreetMap Nominatim usage policy (max 1 request per second globally; custom user-agent identification). Use thread-safe global locks to throttle concurrent threads and protect periodic file flushes to `geocoding_cache.csv`.

**Scale/Scope**: ~2,000 camera locations retrieved via the Minnesota 511 GraphQL endpoint.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Direct API Querying** — Compliant. GraphQL endpoint is untouched.
- **Principle II: CSV Data Persistence** — Compliant. Appends coordinates directly to the CSV output.
- **Principle III: Logging and Observability** — Compliant. Standard logging library is used. Dynamic progress updates are reported cleanly using `tqdm`.
- **Principle IV: Robust Error Handling** — Compliant. Handles connection issues, rate limits, and geocoding failures safely inside workers without crashing the thread pool. Saves cache periodically to prevent progress loss upon interruption.
- **Principle V: Minimal Dependencies** — Compliant. Uses `concurrent.futures.ThreadPoolExecutor` and standard threading locks to manage parallelism without heavy asynchronous frameworks. `tqdm` and `geopy` are added external dependencies, approved by clarification.

## Project Structure

### Documentation (this feature)

```text
specs/001-geocode-camera-locations/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
└── quickstart.md        # Phase 1 output (/speckit-plan command)
```

### Source Code

```text
.
├── .specify/
├── specs/
│   └── 001-geocode-camera-locations/
├── pyproject.toml
├── scrape_cameras.py
├── main.py
└── mn_cameras.csv
```

**Structure Decision**: Single project layout. The scraper script `scrape_cameras.py` will be updated to include the geocoding and caching logic.
