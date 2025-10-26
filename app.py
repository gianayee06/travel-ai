# app.py — TravelBuddy AI (Eco Mode, Mood selector, Google demo, Points/Profile panels)
import streamlit as st
from datetime import date, datetime, timedelta

from api_helpers import *
import json

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="TravelBuddy AI", page_icon="✈️", layout="wide")

# ---------- SESSION DEFAULTS ----------
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "points" not in st.session_state:
    st.session_state.points = 0
if "results" not in st.session_state:
    st.session_state.results = None
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "local_reviews" not in st.session_state:
    st.session_state.local_reviews = []
if "eco_mode" not in st.session_state:
    st.session_state.eco_mode = False
if "google_connected" not in st.session_state:
    st.session_state.google_connected = False
# Control for Local Contributor popup
if "show_local_contrib" not in st.session_state:
    st.session_state.show_local_contrib = False

# ---------- SIGN-UP / SIGN-IN ----------
if not st.session_state.user_authenticated:
    st.title("✈️ Welcome to TravelBuddy AI")
    st.markdown("Your AI-powered travel assistant for smarter, easier trip planning!")

    choice = st.radio("Get started:", ["Sign Up", "Sign In"], horizontal=True)

    if choice == "Sign Up":
        st.subheader("Create Your Free Account")
        with st.form("signup_form"):
            c1, c2 = st.columns(2)
            first_name = c1.text_input("First Name")
            last_name = c2.text_input("Last Name")

            c3, c4 = st.columns(2)
            age = c3.number_input("Age", min_value=0, max_value=120, step=1)
            email = c4.text_input("Email")

            c5, c6 = st.columns(2)
            phone = c5.text_input("Phone Number")
            country = c6.text_input("Resident Country")

            submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not all([first_name, last_name, email, phone, country]):
                st.warning("Please fill out all fields.")
            elif age < 18:
                st.error("You must be at least 18 years old to sign up.")
            else:
                st.session_state.user_authenticated = True
                st.session_state.points += 50

                # Save profile info
                st.session_state.profile = {
                    "first_name": first_name.strip(),
                    "last_name": last_name.strip(),
                    "age": int(age),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "country": country.strip(),
                    "created_at": datetime.utcnow().isoformat()
                }

                st.success(f"🎉 Welcome, {first_name}! You’ve earned a 50-point sign-up bonus!")
                st.balloons()
                st.rerun()

    else:
        st.subheader("Sign In")
        with st.form("signin_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            signin = st.form_submit_button("Sign In")

        if signin:
            if not email or not password:
                st.warning("Please enter both your email and password.")
            else:
                st.session_state.user_authenticated = True
                st.success("Welcome back to TravelBuddy AI!")
                st.balloons()
                st.rerun()

    st.stop()

# ---------- POINTS SYSTEM ----------
POINTS_RULES = {
    "flight_booking": 200,
    "hotel_booking": 150,
    "review": 25,
    "local_review": 50,
}
POINT_TO_DOLLAR = 0.05

def add_points(kind: str, qty: int = 1):
    base = POINTS_RULES.get(kind, 0) * qty
    multiplier = 1.5 if st.session_state.get("eco_mode") else 1.0
    st.session_state.points += int(base * multiplier)

def can_redeem(cost_points: int) -> bool:
    return st.session_state.points >= cost_points

def redeem_points(cost_points: int) -> bool:
    if can_redeem(cost_points):
        st.session_state.points -= cost_points
        return True
    return False

# ---------- LOGO ----------
try:
    col1, col2, col3 = st.columns([1.5, 2, 1])
    with col2:
        st.image("assets/TBLogo.png", width=500)
except Exception:
    pass

# ---------- HEADER TOOLBAR (fallback, always visible) ----------

# ---------- CLICKABLE POINTS / PROFILE ICONS (floating pills) ----------
icons_html = f"""
<style>
  .tb-fab {{
    position: fixed; top: 64px; right: 14px;
    display: flex; gap: 8px; z-index: 100000;
  }}
  .tb-fab a {{
    display: inline-flex; align-items: center; gap: 6px;
    text-decoration: none; background: #111827; color: #fff;
    padding: 6px 10px; border-radius: 999px; font-weight: 700; font-size: 13px;
    box-shadow: 0 2px 10px rgba(0,0,0,.25);
  }}
  .tb-fab a:hover {{ opacity: .95; }}
</style>
<div class="tb-fab">
  <a href="?panel=points">🏆 {st.session_state.points}</a>
  <a href="?panel=profile">👤 Profile</a>
</div>
"""
st.markdown(icons_html, unsafe_allow_html=True)

# ---------- QUERY PARAM HELPERS (compat for older/newer Streamlit) ----------
def _qp_get(name, default=""):
    try:
        # New API (returns str)
        return (st.query_params.get(name, "") or default)
    except Exception:
        # Older API (returns list)
        return (st.experimental_get_query_params().get(name, [default]) or [default])[0]

def _qp_set(mapping):
    try:
        # New API supports direct assignment
        for k, v in mapping.items():
            st.query_params[k] = v
    except Exception:
        cur = st.experimental_get_query_params()
        for k, v in mapping.items():
            cur[k] = v
        st.experimental_set_query_params(**cur)

def _qp_pop(name):
    try:
        if name in st.query_params:
            st.query_params.pop(name)
    except Exception:
        cur = st.experimental_get_query_params()
        if name in cur:
            cur.pop(name)
            st.experimental_set_query_params(**cur)

# ---------- PANEL LOGIC (updated) ----------
panel = (_qp_get("panel", "") or "").lower()

def close_panel():
    _qp_pop("panel")
    st.rerun()

def _panel_wrapper(inner_html: str):
    st.markdown(
        f"""
        <div style="
            position: fixed; top: 110px; right: 14px; max-width: 320px;
            background: #1f2937; color: #fff; padding: 14px 16px;
            border-radius: 12px; box-shadow: 0 12px 28px rgba(0,0,0,.35);
            z-index: 100001;">
            {inner_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Close", key="close_panel_btn"):
        close_panel()

# ---------- DESCRIPTION ----------
st.markdown(
    "<h6 style='text-align: center;'>An intelligent travel assistant that recommends destinations, plans daily schedules, and helps you explore more efficiently — now with EcoPoints and Local Tips.</h6>",
    unsafe_allow_html=True
)

# ---------- CONNECT GOOGLE (DEMO) ----------
with st.expander("🔗 Connect Google (demo)"):
    if not st.session_state.google_connected:
        if st.button("Connect Google Account"):
            st.session_state.google_connected = True
            st.success("Connected (demo). In production, this uses Google OAuth and Places APIs.")
    else:
        st.info("Google account connected (demo).")

# ---------- FAKE BACKEND ----------
def plan_trip(payload: dict):
    """
    Uses backend AI helper functions to generate real trip data
    (flights, hotels, and itinerary) from user input.
    """
    try:
        # 1️⃣ Ensure all expected keys are properly formatted
        backend_payload = {
            "origin": payload.get("origin", "Toronto"),  # default if user didn’t specify
            "destination": payload["destination"].strip(),
            "startDate": payload["start_date"],
            "endDate": payload["end_date"],
            "travelers": int(payload.get("travelers", 1)),
            "budget": float(payload.get("budget", 1000)),
            "mood": payload.get("mood", "balanced"),
            "pace": payload.get("pace", "balanced"),
            "econ": payload.get("eco_mode", False),
        }

        # 2️⃣ Call backend AI helper functions
        flights_raw = get_flight_data(backend_payload)
        hotels_raw = get_hotel_data(backend_payload)
        itinerary_raw = get_itinerary_data(backend_payload)

        # 3️⃣ Try parsing JSON strings from the backend (if returned that way)
        flights = json.loads(flights_raw) if isinstance(flights_raw, str) else flights_raw
        hotels = json.loads(hotels_raw) if isinstance(hotels_raw, str) else hotels_raw
        itinerary = json.loads(itinerary_raw) if isinstance(itinerary_raw, str) else itinerary_raw

        # 4️⃣ Combine everything into a single dictionary
        return {
            "destination": backend_payload["destination"],
            "summary": f"{backend_payload['mood'].capitalize()} trip from {backend_payload['origin']} to {backend_payload['destination']}",
            "flights": flights,
            "hotels": hotels,
            "itinerary": itinerary,
        }

    except Exception as e:
        return {"error": f"Failed to generate trip data: {str(e)}"}

# ---------- FORM ----------
with st.form("planner"):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        destination = st.text_input("Destination", placeholder="e.g., Tokyo")
    with c2:
        start = st.date_input("Start date", value=date.today())
    with c3:
        end = st.date_input("End date", value=date.today())
    with c4:
        travelers = st.number_input("Travelers", min_value=1, max_value=10, value=2)

    c5, c6, c7, c8 = st.columns([1, 1, 1, 2])
    with c5:
        budget = st.number_input("Budget (USD)", min_value=0, value=2000, step=50)
    with c6:
        pace = st.selectbox("Pace", ["relaxed", "balanced", "packed"], index=1)
    with c7:
        mood = st.selectbox("Mood", ["balanced", "relax", "adventure", "culture", "romantic", "surprise"], index=0)
    with c8:
        eco_mode = st.checkbox("🌱 Eco mode (earn 1.5× EcoPoints)", value=st.session_state.eco_mode)

    interests = st.multiselect(
        "Interests",
        ["food", "museums", "nightlife", "nature", "shopping", "history", "beaches", "hiking"]
    )

    submitted = st.form_submit_button("Generate plan")

# ---------- SUBMIT ----------
if submitted:
    if not destination:
        st.warning("Please enter a destination.")
    elif start > end:
        st.warning("Start date must be before end date.")
    else:
        st.session_state.eco_mode = bool(eco_mode)
        payload = {
            "destination": destination.strip(),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "budget": int(budget),
            "travelers": int(travelers),
            "interests": interests,
            "pace": pace,
            "mood": mood,
            "eco_mode": st.session_state.eco_mode,
        }
        with st.spinner("Planning your trip..."):
            st.session_state.results = plan_trip(payload)

# ---------- LOCAL CONTRIBUTOR (opened by a button below the form) ----------
lc_container = st.container()
with lc_container:
    open_lc = st.button("✍️ Open Local Contributor")
    if open_lc:
        st.session_state.show_local_contrib = True
    else:
        st.session_state.show_local_contrib = st.session_state.get("show_local_contrib", False)

# Helper to render the Local Contributor UI anywhere
def render_local_contributor(default_destination: str = ""):
    st.divider()
    st.subheader("Local Contributor — share quick tips & earn points")

    # Choose/confirm the destination for the tip
    dest_input = st.text_input(
        "Destination for your tip",
        value=default_destination,
        placeholder="e.g., Tokyo"
    )

    lc1, lc2, lc3 = st.columns([2, 1, 1])
    with lc1:
        place_name = st.text_input("Place name (cafe, sight, etc.)", placeholder="e.g., Golden Gai Bar")
    with lc2:
        rating = st.slider("Rating", 1, 5, 5)
    with lc3:
        is_local = st.checkbox("I’m a local to this area")

    tip = st.text_area("One-liner tip (max 140 chars)", max_chars=140, placeholder="Best ramen after 10pm…")

    ccc1, ccc2 = st.columns([1, 1])
    with ccc1:
        if st.button("Submit tip & earn points", key="submit_tip_global"):
            if not dest_input or not place_name or not tip:
                st.warning("Please add a destination, a place, and a short tip.")
            else:
                author = (st.session_state.profile.get("first_name","") + " " +
                          st.session_state.profile.get("last_name","")).strip() or "Anonymous"
                st.session_state.local_reviews.append({
                    "destination": dest_input.strip(),
                    "place": place_name.strip(),
                    "tip": tip.strip(),
                    "rating": int(rating),
                    "is_local": bool(is_local),
                    "author": author,
                    "ts": datetime.utcnow().isoformat()
                })
                add_points("local_review" if is_local else "review")
                st.success("Thanks for contributing! Points added.")
    with ccc2:
        if st.button("Close contributor", key="close_lc"):
            st.session_state.show_local_contrib = False

    # Show recent tips for the selected destination (if any)
    dest_sel = (dest_input or "").strip()
    if dest_sel:
        tips_for_dest = [r for r in st.session_state.local_reviews if r.get("destination","") == dest_sel]
        if tips_for_dest:
            st.divider()
            st.subheader(f"Local tips for {dest_sel}")
            for r in reversed(tips_for_dest[-5:]):
                badge = "LOCAL" if r["is_local"] else "VISITOR"
                st.markdown(
                    f"**{r['place']}** — ⭐ {r['rating']} · *{badge}*  \n{r['tip']}  \n<small>by {r['author']}</small>",
                    unsafe_allow_html=True
                )

# If user pressed the button, show the Local Contributor UI (default to current plan’s destination if available)
if st.session_state.show_local_contrib:
    current_dest = (st.session_state.results or {}).get("destination", "")
    with st.container(border=True):
        render_local_contributor(default_destination=current_dest)

# ---------- DISPLAY RESULTS ----------
res = st.session_state.results
if res:
    st.divider()
    st.subheader("Overview")
    st.write(res.get("summary", ""))

    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated Total", f"${res.get('estimated_total_cost', '—')}")
    m2.metric("Days", f"{len(res.get('daily', []))}")
    m3.metric("Destination", res.get("destination", destination or "—"))

    st.divider()
    st.subheader("Bookings & Rewards")

    earn_col, redeem_col = st.columns([2, 1])
    with earn_col:
        st.caption("Earn points by booking through the AI tool")
        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button("Book Flight (via AI) ✈️"):
                add_points("flight_booking")
                st.success("+200 points added!")
        with ec2:
            if st.button("Book Hotel (via AI) 🏨"):
                add_points("hotel_booking")
                st.success("+150 points added!")

    with redeem_col:
        st.caption("Redeem for discounts")
        reward = st.selectbox("Choose a reward", ["💸 $25 off (500 pts)", "💸 $50 off (900 pts)", "💸 $100 off (1600 pts)"])
        cost = {"💸 $25 off (500 pts)": 500, "💸 $50 off (900 pts)": 900, "💸 $100 off (1600 pts)": 1600}[reward]
        if st.button(f"Redeem {cost} pts"):
            if redeem_points(cost):
                st.success(f"Redeemed {cost} points for {reward.split()[0]}!")
            else:
                st.warning("Not enough points to redeem this reward yet.")

    # Daily plan
    st.divider()
    st.subheader("Daily plan")
    for day in res.get("daily", []):
        with st.container(border=True):
            st.markdown(f"**{day.get('date','')} — {day.get('title','')}**")
            for a in day.get("activities", []):
                c1, c2, c3 = st.columns([1, 3, 1])
                c1.write(a.get("time", "—"))
                c2.write(a.get("name", ""))
                # (Keeping your original rendering structure; add more fields here if desired)
