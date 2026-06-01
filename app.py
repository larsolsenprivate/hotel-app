import streamlit as st
import pandas as pd
import requests
import re

# Side opsætning
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

# URL til dit Google Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXV4kL7VWJXV-m5EhgqOOty3nn8OBx9cm8u1K1IsE1ZWGjeJiPBcx3o58NWm5Z0ne8/exec"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit"
KODEORD = "Frankrig2026"

# Login logik
if "logget_ind" not in st.session_state:
    st.session_state.logget_ind = False

if not st.session_state.logget_ind:
    st.title("🔒 Lukket område")
    indtastet_kode = st.text_input("Adgangskode:", type="password")
    if st.button("Log ind"):
        if indtastet_kode == KODEORD:
            st.session_state.logget_ind = True
            st.rerun()
        else:
            st.error("Forkert adgangskode.")
    st.stop()

# Hovedapp
st.title("🇫🇷 Fælles Hoteljagt 2026")

# Input felt til link
booking_link = st.text_input("Indsæt link (Booking.com):")
navn_val = ""
by_val = ""

if booking_link and "booking.com" in booking_link:
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        navn_val = match.group(1).replace("-", " ").title()
    if "ribeauville" in booking_link:
        by_val = "Ribeauvillé"
    elif "chamonix" in booking_link:
        by_val = "Chamonix"
    st.success(f"🤖 Fandt: {navn_val}")

# Formular til at gemme
with st.form("hotel_form", clear_on_submit=True):
    navne_liste = ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"]
    hvem = st.selectbox("Hvem finder det?", options=navne_liste)
    navn = st.text_input("Hotel Navn:", value=navn_val)
    lokation = st.text_input("By:", value=by_val)
    total = st.number_input("Samlet pris (for 8 pers.):", value=12000)
    rating = st.slider("Rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        data = {
            "id": "ny",
            "omraade": "Alsace" if "ribeauville" in booking_link else "Alperne",
            "navn": navn,
            "lokation": lokation,
            "pris": int(total/4/2),
            "rating": rating,
            "bruger": hvem,
            "kommentar": kommentar,
            "link": booking_link
        }
        try:
            response = requests.post(WEB_APP_URL, json=data)
            if response.status_code == 200:
                st.success("🎉 Hotel gemt! (Opdater siden for at se det i tabellen)")
        except Exception as e:
            st.error(f"Fejl ved gem: {e}")

# Tabel og administration
st.write("---")
st.subheader("📊 Oversigt over hoteller")
st.link_button("✏️ Åbn Google Sheet for at rette/slette", SHEET_EDIT_URL)

# Erstat den eksisterende 'try-except' blok med denne for at fejlsøge
try:
    csv_url = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
    df = pd.read_csv(csv_url)
    st.write("Data modtaget fra arket:") # Debugging tekst
    st.dataframe(df)
except Exception as e:
    st.error(f"Kunne ikke hente tabel: {e}")
