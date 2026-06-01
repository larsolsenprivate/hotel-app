import streamlit as st
import pandas as pd
import requests
import re

# 1. SIDE OPSÆTNING (Skal altid stå øverst)
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

st.subheader("📊 Oversigt over hoteller")

# Resten af din kode...
# (Indsæt resten af koden herfra og ned...)
