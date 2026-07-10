# Quickstart & Validation Guide

This guide outlines how to run the camera scraper with geocoding enabled and validate that results are correctly fetched, output, and cached.

## Prerequisites
- Python 3.13+ installed
- Dependencies installed (`pandas`, `requests`, `tqdm`, `pytest`):
  ```bash
  uv pip install -r pyproject.toml
  ```

## Running the Scraper

To run the camera scraper, execute the script from the project root:
```bash
uv run python scrape_cameras.py
```

## Validation Scenarios

### Scenario 1: Initial Run (Uncached / Cache Population)
1. Delete or rename the existing cache CSV file to simulate a first run:
   ```bash
   mv geocoding_cache.csv geocoding_cache.csv.bak
   ```
2. Run the scraper:
   ```bash
   uv run python scrape_cameras.py
   ```
3. **Verify Progress Bar**: Verify a thread-safe `tqdm` progress bar is visible during geocoding.
4. **Verify Output CSV**: Check `mn_cameras.csv`. Verify that `Latitude` and `Longitude` columns are populated with valid float coordinates.
5. **Verify Resumability (Periodic Save)**: Terminate the scraper mid-run. Verify that `geocoding_cache.csv` has been created and contains partial geocoding progress up to the last 50-record boundary.

### Scenario 2: Subsequent Run (Cached / High Performance)
1. Ensure the populated `geocoding_cache.csv` exists.
2. Run the scraper a second time:
   ```bash
   uv run python scrape_cameras.py
   ```
3. **Verify Speed**: The scraper should finish execution in under 10 seconds.
4. **Verify progress**: The progress bar completes instantly (all 100% cache hits resolved from `geocoding_cache.csv`).
5. **Verify Git Tracking**: Run `git status` to verify `geocoding_cache.csv` is tracked by git.

### Scenario 3: Error Handling Validation
1. To simulate a geocoding failure, block or provide an invalid search term for a camera, or temporarily disable network interface during geocoding.
2. Verify that the script logs warnings but does not terminate with an error, and output CSV has blank columns for the failed coordinates.



