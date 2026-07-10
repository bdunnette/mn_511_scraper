import requests
import csv
import json
import logging
import pandas as pd
import os
import time
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError, GeocoderTimedOut, GeocoderServiceError

# Configure geopy Nominatim client
geocoder = Nominatim(
    user_agent="Minnesota511CameraScraper/1.0 (contact: bdunnette@users.noreply.github.com)",
    timeout=10
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Locks for thread safety
cache_lock = threading.Lock()
rate_limit_lock = threading.Lock()
csv_write_lock = threading.Lock()
counter_lock = threading.Lock()

last_request_time = 0.0
geocoded_counter = 0

def fetch_cameras():
    url = "https://511mn.org/api/graphql"
    
    # GraphQL query defined by the site
    query = """
    query ($input: ListArgs!) {
      listCameraViewsQuery(input: $input) {
        cameraViews {
          title
          uri
          url
          sources {
            type
            src
          }
          parentCollection {
            title
            location {
              routeDesignator
            }
          }
        }
        totalRecords
      }
    }
    """
    
    # Variables extracted from site interaction
    variables = {
        "input": {
            "west": -180,
            "south": -85,
            "east": 180,
            "north": 85,
            "sortDirection": "DESC",
            "sortType": "ROADWAY",
            "freeSearchTerm": "",
            "classificationsOrSlugs": [],
            "recordLimit": 2000,
            "recordOffset": 0
        }
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    try:
        logging.info("Fetching camera data from 511mn.org...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        camera_views = data.get('data', {}).get('listCameraViewsQuery', {}).get('cameraViews', [])
        total_records = data.get('data', {}).get('listCameraViewsQuery', {}).get('totalRecords', 0)
        
        logging.info(f"Successfully retrieved {len(camera_views)} / {total_records} cameras.")
        return camera_views
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data: {e}")
        return []
    except (KeyError, ValueError) as e:
        logging.error(f"Unexpected data format: {e}")
        return []

def geocode_location(location_text):
    global last_request_time
    if not location_text:
        return None, None
    
    query = f"{location_text}, Minnesota"
    retries = 3
    backoff = 2.0
    
    # Global thread lock to throttle geocoding requests to 1 req/sec
    with rate_limit_lock:
        now = time.time()
        elapsed = now - last_request_time
        to_sleep = 1.0 - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)
            
        for attempt in range(retries):
            try:
                # Query Nominatim via geopy client
                location = geocoder.geocode(
                    query,
                    exactly_one=True
                )
                last_request_time = time.time()
                if location:
                    return location.latitude, location.longitude
                return None, None
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                if "429" in str(e):
                    logging.warning(f"Rate limited (429) geocoding '{location_text}'. Retrying in {backoff} seconds...")
                else:
                    logging.warning(f"Geocoding request failed for '{location_text}': {e}. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
                last_request_time = time.time()
            except GeopyError as e:
                logging.error(f"Geocoding error for '{location_text}': {e}")
                break
            
    logging.error(f"Failed to geocode location '{location_text}' after {retries} attempts.")
    return None, None

def load_csv_cache(filename="geocoding_cache.csv"):
    if not os.path.exists(filename):
        return {}
    try:
        df = pd.read_csv(filename)
        if "URI" in df.columns and "Latitude" in df.columns and "Longitude" in df.columns:
            valid_df = df.dropna(subset=["Latitude", "Longitude"])
            cache = {}
            for _, row in valid_df.iterrows():
                try:
                    cache[str(row["URI"])] = (float(row["Latitude"]), float(row["Longitude"]))
                except (ValueError, TypeError):
                    continue
            logging.info(f"Loaded {len(cache)} cached camera locations from '{filename}'.")
            return cache
    except Exception as e:
        logging.warning(f"Failed to load CSV cache from '{filename}': {e}. Starting with an empty cache.")
    return {}

def save_csv_cache(cache, filename="geocoding_cache.csv"):
    rows = []
    for uri, (lat, lon) in cache.items():
        rows.append({"URI": uri, "Latitude": lat, "Longitude": lon})
    try:
        df = pd.DataFrame(rows)
        with csv_write_lock:
            df.to_csv(filename, index=False, encoding='utf-8')
    except Exception as e:
        logging.error(f"Failed to save CSV cache to '{filename}': {e}")

def save_to_csv(cameras, filename="mn_cameras.csv"):
    if not cameras:
        logging.warning("No camera data to save.")
        return

    # Flatten the camera data for DataFrame
    rows = []
    for cam in cameras:
        # Extract stream URL
        sources = cam.get('sources', [])
        stream_url = sources[0].get('src', '') if sources else ""

        # Extract roadway and route
        parent = cam.get('parentCollection', {})
        roadway = parent.get('title', '')
        route = parent.get('location', {}).get('routeDesignator', '')

        rows.append({
            "Title": cam.get('title', ''),
            "URI": cam.get('uri', ''),
            "Web URL": cam.get('url', ''),
            "Stream URL": stream_url,
            "Roadway": roadway,
            "Route": route,
            "Latitude": cam.get('latitude'),
            "Longitude": cam.get('longitude')
        })

    try:
        df = pd.DataFrame(rows)
        with csv_write_lock:
            df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Successfully saved {len(df)} cameras to '{filename}' using pandas.")
    except Exception as e:
        logging.error(f"Failed to save CSV file with pandas: {e}")

def geocode_camera(cam, cache, cache_file):
    uri = cam.get("uri")
    
    # 1. Check cache first (URI matching)
    with cache_lock:
        if uri and uri in cache:
            lat, lon = cache[uri]
            cam["latitude"] = lat
            cam["longitude"] = lon
            return cam
        
    # 2. Cache miss - geocode using roadway/title
    parent = cam.get('parentCollection', {})
    roadway = parent.get('title', '')
    location_text = roadway if roadway else cam.get('title', '')
    
    lat, lon = geocode_location(location_text)
    
    if lat is not None and lon is not None:
        cam["latitude"] = lat
        cam["longitude"] = lon
        
        # Add to local cache dict for this run
        with cache_lock:
            cache[uri] = (lat, lon)
            
        # Increment counter and save cache periodically (every 50 records)
        global geocoded_counter
        with counter_lock:
            geocoded_counter += 1
            trigger_save = (geocoded_counter % 50 == 0)
        if trigger_save:
            logging.info(f"Periodically saving geocoding cache progress ({geocoded_counter} new coordinates resolved)...")
            with cache_lock:
                cache_copy = cache.copy()
            save_csv_cache(cache_copy, cache_file)
    else:
        cam["latitude"] = None
        cam["longitude"] = None
        
    return cam

if __name__ == "__main__":
    cameras = fetch_cameras()
    if cameras:
        cache_file = "geocoding_cache.csv"
        # Load geocoding cache from separate CSV
        cache = load_csv_cache(cache_file)
        
        logging.info("Geocoding camera locations...")
        # Concurrently geocode using a ThreadPoolExecutor
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Wrap standard execution with tqdm progress bar
            list(tqdm(
                executor.map(lambda c: geocode_camera(c, cache, cache_file), cameras),
                total=len(cameras),
                desc="Geocoding Cameras"
            ))
            
        # Write final cache back to disk
        save_csv_cache(cache, cache_file)
        
        # Merge cached values to the camera records list for the final CSV dump
        for cam in cameras:
            uri = cam.get("uri")
            if uri in cache:
                lat, lon = cache[uri]
                cam["latitude"] = lat
                cam["longitude"] = lon
            else:
                cam["latitude"] = None
                cam["longitude"] = None
                
    save_to_csv(cameras)





