import pytest
import requests
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_requests_post():
    with patch("requests.post") as mock_post:
        yield mock_post

@pytest.fixture
def mock_nominatim_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "lat": "44.9892",
            "lon": "-92.9774",
            "display_name": "I-694 NB @ 10th St, Minnesota, USA"
        }
    ]
    mock_requests_get.return_value = mock_response
    return mock_requests_get

@pytest.fixture
def mock_nominatim_empty(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_requests_get.return_value = mock_response
    return mock_requests_get

@pytest.fixture
def mock_nominatim_error(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    mock_requests_get.return_value = mock_response
    return mock_requests_get

