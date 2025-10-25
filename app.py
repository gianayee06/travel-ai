# app.py — starter to confirm setup
import streamlit as st

st.set_page_config(page_title="Travel AI (MVP)", page_icon="✈️", layout="centered")

st.title("🌍 Travel AI — MVP")
st.write("If you can see this page, your setup worked!")

with st.form("trip_form"):
    destination = st.text_input("Destination", placeholder="e.g., Tokyo")
    submitted = st.form_submit_button("Generate Plan")

if submitted:
    if not destination:
        st.error("Please enter a destination.")
    else:
        st.success(f"Generating plan for: {destination}")

