import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
import time

# 1. KONFIGURATION
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="wide")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz5CxxGc4SZKNX0ROkVlbO8Ak5DLuzaAlnXbCeeQRl8axhoirFK4t0-p3tQLf3qpR51/exec"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit"
CSV_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
KODEORD = "Frankrig2026"

# Login logik
if "logget_ind" not in st.session_state: st.session_state.logget_ind = False
if not st.session_state.logget_ind:
    st.title("🔒 Lukket område")
    if st.text_input("Adgangskode:", type="password") == KODEORD:
        st.session_state.logget_ind = True
        st.rerun()
    st.stop()

st.title("🇫🇷 Fælles Hoteljagt 2026")

# TABEL SEKTION
st.subheader("📊 Oversigt over hoteller")
col_t1, col_t2 = st.columns([1, 4])
with col_t1:
    if st.button("🔄 Opdatér tabel"): st.cache_data.clear(); st.rerun()
with col_t2:
    st.link_button("✏️ Ret i Google Sheet", SHEET_EDIT_URL)

@st.cache_data(ttl=0) 
def hent_data(url): 
    # Vi henter rå data og tvinger en opdatering med en unik tidsstempel-ID
    url_final = f"{url}&t={time.time()}"
    return pd.read_csv(url_final)

try:
    df = hent_data(CSV_URL)
    df.columns = df.columns.str.strip()
    st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True)
except Exception as e: 
    st.error(f"Fejl ved indlæsning: {e}")

st.write("---")

# FORMULAR SEKTION
st.subheader("➕ Tilføj nyt hotel")
booking_link = st.text_input("Indsæt link fra Booking.com:")
navn_val, by_val, checkin_val, checkout_val, voksne_val = "", "", None, None, 8

if booking_link and "booking.com" in booking_link:
    match = re.search(r'/hotel/fr/([^.]+)', booking_link)
    if match: navn_val = match.group(1).replace("-", " ").title()
    link_lower = booking_link.lower()
    for by_navn in ["Ribeauvillé", "Orbey", "Colmar", "Chamonix", "Annecy", "Strasbourg", "Mulhouse"]:
        if by_navn.lower() in link_lower: by_val = by_navn; break
    
    cin_m = re.search(r'checkin=([\d-]+)', booking_link)
    cout_m = re.search(r'checkout=([\d-]+)', booking_link)
    voks_m = re.search(r'group_adults=(\d+)', booking_link)
    if cin_m: checkin_val = pd.to_datetime(cin_m.group(1))
    if cout_m: checkout_val = pd.to_datetime(cout_m.group(1))
    if voks_m: voksne_val = int(voks_m.group(1))
    st.success("🤖 Data fundet!")

with st.form("hotel_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        hvem = st.selectbox("Hvem?", ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"])
        navn = st.text_input("Hotel:", value=navn_val)
        by = st.text_input("By:", value=by_val)
        adults = st.number_input("Antal voksne:", value=voksne_val)
    with col2:
        omraade = st.radio("Område:", ["Alsace", "Alperne"])
        d_ind = st.date_input("Check-in", value=checkin_val if checkin_val else datetime.today())
        d_ud = st.date_input("Check-ud", value=checkout_val if checkout_val else datetime.today())
        total = st.number_input("Totalpris:", value=12000)
        rating = st.slider("Rating:", 1, 5, 5)
    
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        doegn = (d_ud - d_ind).days
        data = {
            "Område": omraade, "Hotel": navn, "By": by, "Totalpris": total,
            "Rating": rating, "Bruger": hvem, "Kommentar": kommentar,
            "group_adults": adults, "Checkin": str(d_ind), "Checkout": str(d_ud),
            "Døgn": doegn, "Link": booking_link
        }
        try:
            requests.post(WEB_APP_URL, json=data)
            st.success("🎉 Hotel gemt! Tryk på 'Opdatér tabel'.")
        except Exception as e: 
            st.error(f"Fejl: {e}")
