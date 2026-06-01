import streamlit as st
import pandas as pd
import requests
import re

# Side opsætning
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="wide")

# Konfiguration
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXV4kL7VWJXV-m5EhgqOOty3nn8OBx9cm8u1K1IsE1ZWGjeJiPBcx3o58NWm5Z0ne8/exec"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit"
CSV_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
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

# Tabel Sektion
st.subheader("📊 Oversigt over hoteller")
col_tabel_1, col_tabel_2 = st.columns([1, 4])
with col_tabel_1:
    if st.button("🔄 Opdatér data"):
        st.cache_data.clear()
        st.rerun()
with col_tabel_2:
    st.link_button("✏️ Åbn Google Sheet for at rette/slette", SHEET_EDIT_URL)

@st.cache_data(ttl=600)
def hent_data(url):
    return pd.read_csv(url)

try:
    df = hent_data(CSV_URL)
    df['Totalpris'] = pd.to_numeric(df['Totalpris'], errors='coerce')
    df = df.dropna(subset=['Navn'])
    st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True)
except Exception:
    st.info("Ingen hoteller fundet endnu. Tilføj det første hotel nedenfor.")

st.write("---")

# Formular Sektion
st.subheader("➕ Tilføj nyt hotel")
booking_link = st.text_input("Indsæt link fra Booking.com:")

navn_val = ""
by_val = ""

if booking_link and "booking.com" in booking_link:
    # Find navn
    match = re.search(r'/hotel/fr/([^.]+)', booking_link)
    if match:
        navn_val = match.group(1).replace("-", " ").title()
    
    # Smart detektor: Tjekker hele linket for bynavne
    link_lower = booking_link.lower()
    if "ribeauville" in link_lower:
        by_val = "Ribeauvillé"
    elif "chamonix" in link_lower:
        by_val = "Chamonix"
    elif "annecy" in link_lower:
        by_val = "Annecy"
    
    st.success(f"🤖 Fandt: {navn_val} i {by_val}")

with st.form("hotel_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        hvem = st.selectbox("Hvem finder det?", ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"])
        navn = st.text_input("Hotel Navn:", value=navn_val)
        lokation = st.text_input("By:", value=by_val)
    with col2:
        omraade = st.radio("Område:", ["Alsace", "Alperne"])
        total = st.number_input("Totalpris:", value=12000)
        rating = st.slider("Rating:", 1, 5, 5)
    
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        data = {
            "id": "ny",
            "omraade": omraade,
            "navn": navn,
            "lokation": lokation,
            "Totalpris": total,
            "rating": rating,
            "bruger": hvem,
            "kommentar": kommentar,
            "link": booking_link
        }
        try:
            requests.post(WEB_APP_URL, json=data)
            st.success("🎉 Hotel gemt! Tryk på 'Opdatér data'.")
        except Exception as e:
            st.error(f"Fejl ved gem: {e}")
