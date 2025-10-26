# we are using OpenTripMap API to get location data and will be using the documentation from
# https://opentripmap.io/docs
import os #built in module to interact with operating system
import requests # built in module to make and send HTTP requests
import time #built in module to handle time-related tasks
from typing import List, Tuple # built in module to provide type hints, important for clear code and error checking

baseURL = "https://api.opentripmap.com/0.1/en/places/" # Base URL for OpenTripMap API
API_KEY = os.getenv("OPENTRIPMAP_API_KEY")  # Get API key from environment variable
if not API_KEY:
    API_KEY = None

class OpenTripMapAPIError(Exception):
    """exception for OpenTripMap API errors."""
    pass

def _ensure_key():
    """Ensure that the API key is set, otherwise raise an error."""
    if not API_KEY:
        raise OpenTripMapAPIError(
            "OpenTripMap API key not found. Set OPENTRIPMAP_API_KEY environment variable."
        )


def _request_with_retries(url: str, params: dict, max_retries: int = 3, backoff: float = 0.5) -> dict:
    """Make an API request and retry on failure."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif 500 <= response.status_code < 600 or response.status_code == 429:
                # Server or rate limit error — retry
                time.sleep(backoff * attempt)
                continue
            else:
                response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries:
                raise OpenTripMapAPIError(f"Request failed after {max_retries} attempts: {e}")
    raise OpenTripMapAPIError(f"HTTP {response.status_code}: {response.text}")


def get_city_coords(city_name: str) -> Tuple[float, float]:
    """Get latitude and longitude of a given city."""
    _ensure_key()
    url = f"{baseURL}/geoname"
    params = {"name": city_name, "apikey": API_KEY}
    data = _request_with_retries(url, params)
    lat = data.get("lat")
    lon = data.get("lon")
    if lat is None or lon is None:
        raise OpenTripMapAPIError(f"Could not find coordinates for city '{city_name}'. Response: {data}")
    return float(lat), float(lon)


def get_attractions(lat: float, lon: float, radius: int = 1000, limit: int = 20) -> List[str]:
    """Fetch a list of attractions around given coordinates."""
    _ensure_key()
    url = f"{baseURL}/radius"
    params = {
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": limit,
        "rate": 3,
        "format": "json",
        "apikey": API_KEY
    }
    data = _request_with_retries(url, params)
    if not isinstance(data, list):
        raise OpenTripMapAPIError(f"Unexpected response format for radius search: {data}")

    names = [item.get("name") for item in data if item.get("name")]
    return names


def get_attractions_for_city(city_name: str, radius: int = 1000, limit: int = 20) -> List[str]:
    """Fetch top attractions for a city."""
    lat, lon = get_city_coords(city_name)
    return get_attractions(lat, lon, radius=radius, limit=limit)


# Placeholder functions for future development
def generate_flight_options( origin="Toronto", destination="Barcelona",
startDate="2025-06-15", endDate="2025-06-25", travelers=2, budget=3500,
mood="culture", pace="balanced", econ=True ):
    return []
def generate_trip_idea(destination):
    pass

def generate_flight_options(origin, destination, date, econ=False):
    pass

def generate_hotel_recommendations():
    pass

def analyze_sentiment(text):
    pass

def summarize_text(text, max_words=100):
    pass


# ----------------- MAIN EXECUTION -----------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch attractions from OpenTripMap")
    parser.add_argument("city", help="City name, e.g. 'Toronto' or 'Paris'")
    parser.add_argument("--radius", type=int, default=1000, help="Search radius in meters")
    parser.add_argument("--limit", type=int, default=20, help="Max number of POIs to fetch")
    args = parser.parse_args()

    try:
        results = get_attractions_for_city(args.city, radius=args.radius, limit=args.limit)
        print(f"Top {len(results)} attractions near {args.city}:")
        for i, name in enumerate(results, 1):
            print(f"{i}. {name}")
    except OpenTripMapAPIError as e:
        print("Error:", e)


