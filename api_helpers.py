from typing import Dict
from ai_helpers import (
    generate_flight_options,
    generate_hotel_options,
    generate_itinerary,
    summarize_text,
    analyze_sentiment,
)

def get_flight_data(params: Dict) -> str:
    return generate_flight_options(
        origin=params.get("origin", ""),
        destination=params.get("destination", ""),
        startDate=params.get("startDate", ""),
        endDate=params.get("endDate", ""),
        travelers=int(params.get("travelers", 1)),
        budget=float(params.get("budget", 1000)),
        mood=params.get("mood", "balanced"),
        pace=params.get("pace", "balanced"),
        econ=bool(params.get("econ", False)),
    )

def get_hotel_data(params: Dict) -> str:
    return generate_hotel_options(
        origin=params.get("origin", ""),
        destination=params.get("destination", ""),
        startDate=params.get("startDate", ""),
        endDate=params.get("endDate", ""),
        travelers=int(params.get("travelers", 1)),
        budget=float(params.get("budget", 1000)),
        mood=params.get("mood", "balanced"),
        pace=params.get("pace", "balanced"),
        econ=bool(params.get("econ", False)),
    )

def get_itinerary_data(params: Dict) -> str:
    return generate_itinerary(
        origin=params.get("origin", ""),
        destination=params.get("destination", ""),
        startDate=params.get("startDate", ""),
        endDate=params.get("endDate", ""),
        travelers=int(params.get("travelers", 1)),
        budget=float(params.get("budget", 1000)),
        mood=params.get("mood", "balanced"),
        pace=params.get("pace", "balanced"),
        econ=bool(params.get("econ", False)),
        flight_price_total=params.get("flight_price_total"),
        nightly_price_cap=params.get("nightly_price_cap"),
    )