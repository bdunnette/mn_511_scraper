import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from scrape_cameras import load_csv_cache, geocode_camera, save_to_csv

def test_load_csv_cache_non_existent(tmp_path):
    test_csv = tmp_path / "non_existent.csv"
    cache = load_csv_cache(str(test_csv))
    assert cache == {}

def test_load_csv_cache_valid(tmp_path):
    test_csv = tmp_path / "test_cameras.csv"
    df = pd.DataFrame([
        {"URI": "uri1", "Latitude": 45.0, "Longitude": -93.0},
        {"URI": "uri2", "Latitude": None, "Longitude": None},
        {"URI": "uri3", "Latitude": 46.0, "Longitude": -94.0}
    ])
    df.to_csv(test_csv, index=False)
    
    cache = load_csv_cache(str(test_csv))
    assert cache == {"uri1": (45.0, -93.0), "uri3": (46.0, -94.0)}

def test_geocode_camera_cache_hit():
    cam = {"uri": "uri1", "title": "Camera 1", "parentCollection": {"title": "Roadway 1"}}
    cache = {"uri1": (45.0, -93.0)}
    
    with patch("scrape_cameras.geocode_location") as mock_geocode:
        res = geocode_camera(cam, cache, "dummy.csv")
        assert res["latitude"] == 45.0
        assert res["longitude"] == -93.0
        mock_geocode.assert_not_called()

def test_geocode_camera_cache_miss():
    cam = {"uri": "uri1", "title": "Camera 1", "parentCollection": {"title": "Roadway 1"}}
    cache = {}
    
    with patch("scrape_cameras.geocode_location", return_value=(45.0, -93.0)) as mock_geocode:
        res = geocode_camera(cam, cache, "dummy.csv")
        assert res["latitude"] == 45.0
        assert res["longitude"] == -93.0
        assert cache["uri1"] == (45.0, -93.0)
        mock_geocode.assert_called_once_with("Roadway 1")
