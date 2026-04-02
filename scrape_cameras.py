import requests
import csv
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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

import pandas as pd

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
            "Route": route
        })

    try:
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Successfully saved {len(df)} cameras to '{filename}' using pandas.")
        
    except Exception as e:
        logging.error(f"Failed to save CSV file with pandas: {e}")

if __name__ == "__main__":
    cameras = fetch_cameras()
    save_to_csv(cameras)
