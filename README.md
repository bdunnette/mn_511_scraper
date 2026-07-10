# Minnesota 511 Camera Scraper

This scraper fetches traffic camera metadata directly from the 511mn.org GraphQL API, geocodes the camera locations, and persists them to a structured CSV format.

## Features

- **Direct API Fetching**: Queries the 511mn.org GraphQL backend to fetch structured records efficiently in bulk.
- **Geocoding**: Resolves camera roadway/intersection text to latitude and longitude coordinates using the OpenStreetMap Nominatim API.
- **Geocoding Cache**: Stores successfully geocoded coordinate results in `geocoding_cache.json` to minimize external queries and avoid API blocks.
- **Git-Tracked Cache**: The cache file is checked directly into Git to share resolved coordinate mappings across environments.
- **Concurrently Executed**: Leverages a python thread pool (`ThreadPoolExecutor`) for concurrent execution. Cache hits run concurrently in parallel, while cache misses are thread-safe and throttled to 1 request/second globally.
- **Visual Progress**: Dynamic, thread-safe progress visualization using a `tqdm` progress bar.

## Installation

Ensure `uv` is installed, then install dependencies:
```bash
uv pip install -r pyproject.toml
```

## Running the Scraper

To run the camera scraper:
```bash
uv run python scrape_cameras.py
```
This generates `mn_cameras.csv` inside the project root directory, containing coordinate fields.

## Test Suite

To run the tests:
```bash
uv run python -m pytest
```

