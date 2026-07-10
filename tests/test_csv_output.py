import os
import pandas as pd
from scrape_cameras import save_to_csv

def test_save_to_csv_includes_coordinates(tmp_path):
    test_csv = tmp_path / "test_cameras.csv"
    cameras = [
        {
            "title": "Camera 1",
            "uri": "uri1",
            "url": "url1",
            "sources": [{"src": "stream1"}],
            "parentCollection": {
                "title": "Roadway 1",
                "location": {"routeDesignator": "Route 1"}
            },
            "latitude": 45.1234,
            "longitude": -93.5678
        },
        {
            "title": "Camera 2",
            "uri": "uri2",
            "url": "url2",
            "sources": [],
            "parentCollection": {},
            "latitude": None,
            "longitude": None
        }
    ]

    save_to_csv(cameras, filename=str(test_csv))
    
    assert os.path.exists(test_csv)
    df = pd.read_csv(test_csv)
    
    # Assert columns exist
    assert "Latitude" in df.columns
    assert "Longitude" in df.columns
    
    # Assert data is correct
    assert df.loc[0, "Latitude"] == 45.1234
    assert df.loc[0, "Longitude"] == -93.5678
    assert pd.isna(df.loc[1, "Latitude"])
    assert pd.isna(df.loc[1, "Longitude"])
