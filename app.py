import streamlit as st
import pandas as pd
import requests
import re

# 1. SIDE OPSÆTNING (Skal altid ligge øverst)
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="wide")

# 2. KONFIGURATION
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXV4kL7VWJXV-m5EhgqOOty3nn8OBx9cm8u1K1IsE1ZWGjeJiPBcx3o58NWm5Z0ne8/exec"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit"
CSV_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/gviz/tq?tqx=out:csv"
KODEORD = "Frankrig2026"

# 3. LOGIN LOGIK
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

# 4. HOVEDAPP
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
    df['Pris'] = pd.to_numeric(df['Pris'], errors='coerce')
    df = df.dropna(subset=['Navn'])
    st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True)
except Exception:
    st.info("Ingen hoteller fundet endnu eller arket er tomt.")

st.write("---")

# Formular Sektion
st.subheader("➕ Tilføj nyt hotel")
booking_link = st.text_input("Indsæt link fra Booking.com (for automatisk udfyldning):")
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

with st.form("hotel_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        hvem = st.selectbox("Hvem finder det?", ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"])
        navn = st.text_input("Hotel Navn:", value=navn_val)
        lokation = st.text_input("By:", value=by_val)
    with col2:
        omraade = st.radio("Område:", ["Alsace", "Alperne"])
        total = st.number_input("Samlet pris (for 8 pers.):", value=12000)
        rating = st.slider("Rating:", 1, 5, 5)
    
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        data = {
            "id": "ny",
            "omraade": omraade,
            "navn": navn,
            "lokation": lokation,
            "pris": int(total/4/2) if omraade == "Alsace" else int(total/4/6),
            "rating": rating,
            "bruger": hvem,
            "kommentar": kommentar,
            "link": booking_link
        }
        try:
            response = requests.post(WEB_APP_URL, json=data)
            if response.status_code == 200:
                st.success("🎉 Hotel gemt! Tryk på 'Opdatér data' for at se det.")
        except Exception as e:
            st.error(f"Fejl ved gem: {e}")
