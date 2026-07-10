# Research: Geocoding and Caching Strategy

## Decision: Direct Nominatim API Queries with CSV Caching and Periodic Saving

### 1. Geocoding Service
- **Chosen**: OpenStreetMap Nominatim API accessed via the `geopy` library.
- **Rationale**: 
  - Free to use, no API key required.
  - Returns precise latitude and longitude.
  - Instantiated using the `user_agent` constructor parameter to comply with usage policies.
- **Constraints**:
  - Requires a custom, descriptive `User-Agent`.
  - Usage policy restricts queries to a maximum of 1 request per second.
  - Multi-threaded execution will be used. Thread safety for Nominatim calls is enforced using a global threading Lock that spaces out API requests by at least 1.0 second globally, while cache hits remain instant and concurrent.

### 2. Cache Mechanism
- **Chosen**: Separate local CSV file (`geocoding_cache.csv`), tracked directly in Git.
- **Rationale**:
  - Keeps the main scraper output `mn_cameras.csv` clean of intermediate/incomplete geocoding runs.
  - Cache coordinates are loaded from `geocoding_cache.csv` at startup, mapping `URI` -> `(Latitude, Longitude)`.
  - Tracked in Git to share already-resolved coordinate mappings.

### 3. Concurrency & Periodic Saving
- **Strategy**: Implement a global `threading.Lock` protecting Nominatim search API calls and another lock protecting `geocoding_cache.csv` file writes. Each cache miss will acquire the rate-limiting lock, wait for the global throttling interval (at least 1.0 second since the last request), and fire.
- **Resumability**: To prevent losing geocoding progress if execution is interrupted, the threads will trigger a thread-safe cache write to `geocoding_cache.csv` after every 50 newly geocoded items. Upon file save, a thread-safe subprocess command block stages, commits (`[skip ci]` suffix in message), and pushes `geocoding_cache.csv` to the Git repository.
- **Progress Reporting**: `tqdm` library is utilized to render a dynamic thread-safe progress bar. At the end of the run, pandas merges cache coordinates into the main camera dataframe and outputs it to `mn_cameras.csv`.


