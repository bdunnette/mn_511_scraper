import pytest
from unittest.mock import patch, MagicMock
from scrape_cameras import geocode_location
from geopy.exc import GeocoderTimedOut

def test_geocode_location_success():
    mock_location = MagicMock()
    mock_location.latitude = 44.9892
    mock_location.longitude = -92.9774
    
    with patch("scrape_cameras.geocoder.geocode", return_value=mock_location) as mock_geocode:
        lat, lon = geocode_location("I-694 NB @ 10th St")
        assert lat == 44.9892
        assert lon == -92.9774
        mock_geocode.assert_called_once_with(
            "I-694 NB @ 10th St, Minnesota",
            exactly_one=True
        )

def test_geocode_location_empty():
    with patch("scrape_cameras.geocoder.geocode", return_value=None) as mock_geocode:
        lat, lon = geocode_location("Unknown Location")
        assert lat is None
        assert lon is None

def test_geocode_location_error():
    with patch("scrape_cameras.geocoder.geocode", side_effect=GeocoderTimedOut("Timeout")) as mock_geocode:
        lat, lon = geocode_location("Error Location")
        assert lat is None
        assert lon is None
        assert mock_geocode.call_count == 3

