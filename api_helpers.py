from ai_helpers import *
import json


def get_flight_data(params: dict) -> str:
    """
    Calls the AI helper to generate flight options.
    Expects a dictionary with all required fields.
    """
    try:
        result = generate_flight_options(
            origin=params.get("origin", ""),
            destination=params.get("destination", ""),
            startDate=params.get("startDate", ""),
            endDate=params.get("endDate", ""),
            travelers=int(params.get("travelers", 1)),
            budget=float(params.get("budget", 1000)),
            mood=params.get("mood", "balanced"),
            pace=params.get("pace", "balanced"),
            econ=params.get("econ", False),
        )
        return result
    except Exception as e:
        return f"Error generating flight data: {e}"


def get_hotel_data(params: dict) -> str:
    """
    Calls the AI helper to generate hotel options.
    Expects a dictionary with all required fields.
    """
    try:
        result = generate_hotel_options(
            origin=params.get("origin", ""),
            destination=params.get("destination", ""),
            startDate=params.get("startDate", ""),
            endDate=params.get("endDate", ""),
            travelers=int(params.get("travelers", 1)),
            budget=float(params.get("budget", 1000)),
            mood=params.get("mood", "balanced"),
            pace=params.get("pace", "balanced"),
            econ=params.get("econ", False),
        )
        return result
    except Exception as e:
        return f"Error generating hotel data: {e}"


def get_itinerary_data(params: dict) -> str:
    """
    Calls the AI helper to generate a travel itinerary.
    Expects a dictionary with all required fields.
    """
    try:
        result = generate_itinerary(
            origin=params.get("origin", ""),
            destination=params.get("destination", ""),
            startDate=params.get("startDate", ""),
            endDate=params.get("endDate", ""),
            travelers=int(params.get("travelers", 1)),
            budget=float(params.get("budget", 1000)),
            mood=params.get("mood", "balanced"),
            pace=params.get("pace", "balanced"),
            econ=params.get("econ", False),
        )
        return result
    except Exception as e:
        return f"Error generating itinerary data: {e}"


# ----------------- TESTING LOCALLY -----------------
if __name__ == "__main__":
    sample_params = {
        "origin": "Toronto",
        "destination": "Lisbon",
        "startDate": "2025-06-01",
        "endDate": "2025-06-10",
        "travelers": 2,
        "budget": 4000,
        "mood": "romantic",
        "pace": "balanced",
        "econ": True,
    }

    print("\n✈️ Flights:\n", get_flight_data(sample_params))
    print("\n🏨 Hotels:\n", get_hotel_data(sample_params))
    print("\n🗺️ Itinerary:\n", get_itinerary_data(sample_params))