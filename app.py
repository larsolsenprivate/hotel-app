import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXV4kL7VWJXV-m5EhgqOOty3nn8OBx9cm8u1K1IsE1ZWGjeJiPBcx3o58NWm5Z0ne8/exec"
KODEORD = "Frankrig2026"

# ... [Log-in kode forbliver den samme] ...

st.title("🇫🇷 Fælles Hoteljagt 2026")

booking_link = st.text_input("Indsæt link (Booking.com):")
navn_val = ""
by_val = ""

if booking_link and "booking.com" in booking_link:
    # Finder navn
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        navn_val = match.group(1).replace("-", " ").title()
        
    # Her leder vi efter bynavne i linket (hvis de findes som søgeparametre)
    # Dette er en simpel metode
    if "search_ribeauville" in booking_link:
        by_val = "Ribeauvillé"
    elif "chamonix" in booking_link:
        by_val = "Chamonix"
    
    if navn_val: st.success(f"🤖 Fandt: {navn_val}")

with st.form("hotel_form", clear_on_submit=True):
    navn = st.text_input("Hotel Navn:", value=navn_val)
    lokation = st.text_input("By:", value=by_val)
    # ... resten af formularen ...
    
    if st.form_submit_button("Gem hotel"):
        # ... (Requests koden fra før) ...

st.write("---")
st.subheader("📊 Oversigt over hoteller")

try:
    # Denne URL henter data fra dit ark som CSV
    csv_url = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
    df = pd.read_csv(csv_url)
    st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True)
except:
    st.info("Ingen hoteller fundet endnu.")
