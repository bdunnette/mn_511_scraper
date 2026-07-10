# Data Model: Geocoded Cameras and Cache Schema

This document details the data structures for the persistent geocoding cache and the updated output CSV format.

## 1. Local Cache Schema (`geocoding_cache.json`)

The local cache is serialized as a JSON object where the keys are the camera's location text (Title/Roadway), and the values are objects containing coordinates.

```json
{
  "I-694: I-94 WB E Jct I-494": {
    "lat": 44.9537,
    "lon": -93.0898,
    "geocoded_at": "2026-07-10T12:00:00Z"
  },
  "I-694: I-694 NB @ 10th St": {
    "lat": 44.9892,
    "lon": -92.9774,
    "geocoded_at": "2026-07-10T12:05:00Z"
  }
}
```

### Fields

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `lat` | Float | The geocoded latitude coordinate (-90.0 to 90.0). |
| `lon` | Float | The geocoded longitude coordinate (-180.0 to 180.0). |
| `geocoded_at` | String | ISO 8601 UTC timestamp of when the coordinates were retrieved from the external service. |

## 2. Updated Output CSV Schema (`mn_cameras.csv`)

The output file format remains a CSV, with two new columns appended at the end.

| Column | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| Title | String | `I-694: I-694 NB @ 10th St` | The camera title. |
| URI | String | `camera/489545/225285580` | Unique resource identifier. |
| Web URL | String | `https://public.carsprogram.org/cameras/MN/C725` | Web URL for the camera stream webpage. |
| Stream URL | String | `https://video.dot.state.mn.us/public/C725.stream/playlist.m3u8` | Direct stream URL. |
| Roadway | String | `I-694: I-694 NB @ 10th St` | The roadway collection name. |
| Route | String | `I-694` | Route designator. |
| **Latitude** | Float (Nullable) | `44.9892` | Geocoded latitude. Blank if geocoding fails. |
| **Longitude** | Float (Nullable) | `-92.9774` | Geocoded longitude. Blank if geocoding fails. |
