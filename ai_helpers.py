import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars from .env if present
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # safe default

_client = None
def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT_ID)
    return _client

def generate_text(prompt: str, temperature: float = 0.5, model: str = OPENAI_MODEL) -> str:
    """Thin wrapper for OpenAI Chat Completions."""
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are TravelBuddy AI: concise, structured, and helpful."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

def summarize_text(text: str, max_words: int = 100) -> str:
    prompt = f"Summarize the following text in under {max_words} words.\n\n{text}"
    return generate_text(prompt, temperature=0.2)

def analyze_sentiment(text: str) -> str:
    prompt = f"Classify the sentiment of this text as one of: Positive, Neutral, or Negative.\n\nText: {text}\n\nAnswer with just the label."
    return generate_text(prompt, temperature=0.0)

def generate_flight_options(origin: str, destination: str, startDate: str, endDate: str,
                            travelers: int, budget: float, mood: str, pace: str, econ: bool) -> str:
    eco_line = "Prioritize lower CO2 flights where possible and mark them with (eco)." if econ else ""
    prompt = f"""You are a travel agent. Propose 3–5 flight options.
Origin: {origin}
Destination: {destination}
Dates: {startDate} to {endDate}
Travelers: {travelers}
Total budget (all travelers): ${budget:.2f}
Mood: {mood}
Pace: {pace}
{eco_line}

Return a clean numbered list. For each option include: Airline, route, depart/arrive times (local), layovers, rough price (USD), and 1-line rationale. Keep each option to ~2 lines.
"""
    return generate_text(prompt, temperature=0.6)

def generate_hotel_options(origin: str, destination: str, startDate: str, endDate: str,
                           travelers: int, budget: float, mood: str, pace: str, econ: bool) -> str:
    eco_line = "Prefer eco-certified properties (LEED/Green Key/etc.) and mark with (eco)." if econ else ""
    prompt = f"""Recommend 3–5 hotel/lodging options in {destination}.
Trip: {startDate} to {endDate} | Travelers: {travelers} | Mood: {mood} | Pace: {pace}
Overall trip budget: ${budget:.2f}. Assume ~40% of budget can go to lodging.
{eco_line}

Return a numbered list with: Property name, area, nightly price (USD) and total stay estimate, vibe/fit (1 line).
"""
    return generate_text(prompt, temperature=0.6)

def generate_itinerary(origin: str, destination: str, startDate: str, endDate: str,
                       travelers: int, budget: float, mood: str, pace: str, econ: bool) -> str:
    eco_line = "Favor low-impact transport (walk/transit/bike) and local/eco experiences where it fits." if econ else ""
    prompt = f"""Build a concise daily itinerary for a trip.
Origin: {origin} → Destination: {destination}
Dates: {startDate} to {endDate} | Travelers: {travelers}
Budget: ${budget:.2f} total | Mood: {mood} | Pace: {pace}
{eco_line}

Format by day (Day 1, Day 2...). For each day include 3–5 key activities/meals with quick tips and rough costs (USD). Keep it scannable.
"""
    return generate_text(prompt, temperature=0.5)
