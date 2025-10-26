# app.py — TravelBuddy AI (integrated)
import streamlit as st
from datetime import date
from api_helpers import get_flight_data, get_hotel_data, get_itinerary_data

st.set_page_config(page_title="TravelBuddy AI", page_icon="✈️", layout="wide")
#st.caption("💡 Tip: Toggle Eco Mode in the top bar to get sustainable picks!")

# ---- Session defaults ----
def init_state():
    defaults = {
        "user_authenticated": False,
        "points": 0,
        "page": "Home",
        "results": {"flights": "", "hotels": "", "itinerary": ""},
        "eco_mode": False,
        "mood": "balanced",
        "pace": "balanced",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

POINTS_RULES = {"flight_booking": 200, "hotel_booking": 150, "review": 25, "local_review": 50}
POINT_TO_DOLLAR = 0.05

def add_points(kind: str, qty: int = 1):
    base = POINTS_RULES.get(kind, 0) * qty
    multiplier = 1.5 if st.session_state.get("eco_mode") else 1.0
    st.session_state.points += int(base * multiplier)

# ---- UI components ----
def topbar():
    cols = st.columns([6,1,1,1])
    with cols[0]:
        st.markdown("## TravelBuddy AI")
    with cols[1]:
        if st.button("🏆 Points"):
            st.session_state.page = "Points"
    with cols[2]:
        if st.button("👤 Profile"):
            st.session_state.page = "Profile"
    with cols[3]:
        st.session_state.eco_mode = st.toggle("Eco", value=st.session_state.eco_mode, help="Prioritize eco-friendly picks")

def plan_form():
    with st.form("planner"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            origin = st.text_input("Origin", placeholder="Toronto (YYZ)")
        with c2:
            destination = st.text_input("Destination", placeholder="Lisbon (LIS)")
        with c3:
            start = st.date_input("Start", value=date.today())
        with c4:
            end = st.date_input("End", value=date.today())

        c5, c6, c7, c8 = st.columns([1,1,1,1])
        with c5:
            travelers = st.number_input("Travelers", min_value=1, value=1, step=1)
        with c6:
            budget = st.number_input("Budget (USD)", min_value=100.0, value=2000.0, step=100.0)
        with c7:
            mood = st.selectbox("Mood", ["balanced", "adventurous", "relaxed", "romantic", "family"], index=0)
        with c8:
            pace = st.selectbox("Pace", ["balanced", "slow", "fast"], index=0)

        submitted = st.form_submit_button("Generate Plan")

    if submitted:
        params = {
            "origin": origin, "destination": destination,
            "startDate": str(start), "endDate": str(end),
            "travelers": travelers, "budget": budget,
            "mood": mood, "pace": pace, "econ": st.session_state.eco_mode,
        }
        with st.spinner("Thinking up options..."):
            st.session_state.results["flights"] = get_flight_data(params)
            st.session_state.results["hotels"] = get_hotel_data(params)
            st.session_state.results["itinerary"] = get_itinerary_data(params)
        add_points("review", 1)  # small reward for planning

def page_home():
    plan_form()
    r = st.session_state.results
    if any(r.values()):
        st.markdown("## Your AI Travel Plan")

        # Two-column layout for Flights and Hotels
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Flights")
            st.info(r["flights"] or "_No results yet._")

        with col2:
            st.markdown("### Hotels")
            st.success(r["hotels"] or "_No results yet._")

        st.markdown("---")
        st.markdown("### Itinerary")
        st.warning(r["itinerary"] or "_No results yet._")

        

def page_points():
    st.markdown("### 🏆 Your Points")
    pts = st.session_state.points
    st.metric("Total Points", pts)
    st.caption(f"Estimated value: ${pts*POINT_TO_DOLLAR:.2f} in credits")


def page_profile():
    st.markdown("### 👤 Profile")
    st.write("Signed in:", "Yes" if st.session_state.user_authenticated else "Guest")
    st.write("Eco mode:", "On" if st.session_state.eco_mode else "Off")
    st.write("Mood:", st.session_state.mood)
    st.write("Pace:", st.session_state.pace)

def router():
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Points":
        page_points()
    elif st.session_state.page == "Profile":
        page_profile()

def main():
    init_state()
    topbar()
    router()

if __name__ == "__main__":
    main()
