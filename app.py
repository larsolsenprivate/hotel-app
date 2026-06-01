import streamlit as st
import requests
import re

st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzXV4kL7VWJXV-m5EhgqOOty3nn8OBx9cm8u1K1IsE1ZWGjeJiPBcx3o58NWm5Z0ne8/exec"
KODEORD = "Frankrig2026"

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

st.title("🇫🇷 Fælles Hoteljagt 2026")

# Hent data fra link
booking_link = st.text_input("Indsæt link (Booking.com):")
forslag_navn = ""
forslag_by = ""

if booking_link and "booking.com" in booking_link:
    # Finder navn i linket
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        forslag_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt hotel: {forslag_navn}")

# FORMULAR
with st.form("hotel_form", clear_on_submit=True):
    navne_liste = ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"]
    hvem = st.selectbox("Hvem finder det?", options=navne_liste)
    navn = st.text_input("Hotel Navn:", value=forslag_navn)
    omraade = st.radio("Område:", ["Alsace", "Alperne"])
    lokation = st.text_input("By:", value=forslag_by)
    total = st.number_input("Samlet pris (for 8 pers.):", value=12000)
    rating = st.slider("Rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem hotel"):
        data = {
            "id": "ny",
            "omraade": omraade,
            "navn": navn,
            "lokation": lokation,
            "pris": int(total/4/2) if omraade=="Alsace" else int(total/4/6),
            "rating": rating,
            "bruger": hvem,
            "kommentar": kommentar,
            "link": booking_link
        }
        try:
            response = requests.post(WEB_APP_URL, json=data)
            if response.status_code == 200:
                st.success("🎉 Hotel gemt!")
            else:
                st.error("Kunne ikke gemme.")
        except Exception as e:
            st.error(f"Fejl: {e}")
