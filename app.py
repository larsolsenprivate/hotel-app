import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
import time

# --- KONFIGURATION ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz5CxxGc4SZKNX0ROkVlbO8Ak5DLuzaAlnXbCeeQRl8axhoirFK4t0-p3tQLf3qpR51/exec"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit"
CSV_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
KODEORD = "Frankrig2026"

st.set_page_config(page_title="Hoteljagt 2026", layout="wide")

# --- LOGIN ---
if "logget_ind" not in st.session_state: st.session_state.logget_ind = False
if not st.session_state.logget_ind:
    if st.text_input("Adgangskode:", type="password") == KODEORD:
        st.session_state.logget_ind = True
        st.rerun()
    st.stop()

# --- TABEL (MED FEJLHÅNDTERING) ---
st.title("🇫🇷 Fælles Hoteljagt 2026")
if st.button("🔄 Opdatér oversigt"): st.cache_data.clear()

@st.cache_data(ttl=0)
def hent_data():
    # Tilføjer tidsstempel for at undgå Google-cache
    return pd.read_csv(f"{CSV_URL}&t={time.time()}")

try:
    df = hent_data()
    # Rens kolonnenavne for usynlige mellemrum
    df.columns = df.columns.str.strip()
    st.dataframe(df, use_container_width=True)
    st.link_button("✏️ Ret data i Google Sheet", SHEET_EDIT_URL)
except Exception as e:
    st.error(f"Kunne ikke hente tabel: {e}")

# --- FORMULAR ---
st.subheader("➕ Tilføj nyt hotel")
booking_link = st.text_input("Indsæt link fra Booking.com:")

# Udtræk kun det sikre
navn_val, cin_val, cout_val, pers_val = "", None, None, 8
if booking_link and "booking.com" in booking_link:
    # Hotelnavn
    match = re.search(r'/hotel/fr/([^.]+)', booking_link)
    if match: navn_val = match.group(1).replace("-", " ").title()
    # Datoer & Personer
    cin = re.search(r'checkin=([\d-]+)', booking_link)
    cout = re.search(r'checkout=([\d-]+)', booking_link)
    pers = re.search(r'group_adults=(\d+)', booking_link)
    if cin: cin_val = pd.to_datetime(cin.group(1))
    if cout: cout_val = pd.to_datetime(cout.group(1))
    if pers: pers_val = int(pers.group(1))

with st.form("hotel_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        hvem = st.selectbox("Hvem?", ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"])
        navn = st.text_input("Hotel:", value=navn_val)
        by = st.text_input("By:") # Manuelt input - ingen hardcoding!
        antal = st.number_input("Antal voksne:", value=pers_val)
    with c2:
        omraade = st.radio("Område:", ["Alsace", "Alperne"])
        d_ind = st.date_input("Check-in", value=cin_val if cin_val else datetime.today())
        d_ud = st.date_input("Check-ud", value=cout_val if cout_val else datetime.today())
        pris = st.number_input("Totalpris:", value=12000)
        rating = st.slider("Rating:", 1, 5, 5)
    
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        doegn = (d_ud - d_ind).days
        data = {
            "Område": omraade, "Hotel": navn, "By": by, "Totalpris": pris,
            "Rating": rating, "Bruger": hvem, "Kommentar": kommentar,
            "group_adults": antal, "Checkin": str(d_ind), "Checkout": str(d_ud),
            "Døgn": doegn, "Link": booking_link
        }
        try:
            requests.post(WEB_APP_URL, json=data)
            st.success("🎉 Hotel gemt!")
        except Exception as e: st.error(f"Fejl: {e}")
