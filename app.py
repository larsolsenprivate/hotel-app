import streamlit as st
import pandas as pd
import re
from shillelagh.backends.apsw.db import connect

st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

# ==============================================================================
# 🔒 SIKKERHED: VÆLG DIN ADGANGSKODE HER:
KODEORD = "Frankrig2026"
# ==============================================================================

# ==============================================================================
# ⚠️ INDSÆT DIT GOOGLE SHEET LINK HERUNDER:
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit?gid=0#gid=0"
# ==============================================================================

if "logget_ind" not in st.session_state:
    st.session_state.logget_ind = False

if not st.session_state.logget_ind:
    st.title("🔒 Lukket område")
    st.write("Dette er en lukket app til herreturen/venneturen 2026. Indtast adgangskode for at fortsætte:")
    
    indtastet_kode = st.text_input("Adgangskode:", type="password")
    
    if st.button("Log ind"):
        if indtastet_kode == KODEORD:
            st.session_state.logget_ind = True
            st.success("Logget ind! Appen indlæses...")
            st.rerun()
        else:
            st.error("Forkert adgangskode. Prøv igen!")
            
    st.stop()


# ==============================================================================
# HERUNDER STARTER SELVE APPEN
# ==============================================================================

try:
    sheet_id = re.search(r"/d/([^/]+)", GOOGLE_SHEET_URL).group(1)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
except:
    st.error("Google Sheet URL'en er ikke gyldig.")
    st.stop()

def hent_data():
    try:
        df = pd.read_csv(csv_url)
        df = df.dropna(how="all")
        return df.to_dict(orient="records")
    except:
        return []

hoteller_liste = hent_data()

st.title("🇫🇷 Fælles Hoteljagt 2026")
st.subheader("Krav: 4 værelser (8 personer) | Max 1.000 kr. pr. person totalt")

fane = st.radio("Vælg område:", ["🍇 Alsace (2 nætter)", "🏔️ Alperne (6 nætter)"])
naetter = 2 if "Alsace" in fane else 6
aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"

st.write("---")
st.subheader("Tilføj nyt sted")

with st.form("nyt_hotel_form", clear_on_submit=True):
    navne_liste = ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"]
    hvem_er_du = st.selectbox("Hvem finder det?", options=navne_liste)
    
    navn = st.text_input("Hotel / Airbnb Navn:")
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    total_regning = st.number_input(f"Samlet pris (For 4 værelser i alle {naetter} nætter i alt):", min_value=0, value=8000)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    booking_link = st.text_input("Indsæt link (Booking.com / Airbnb):", value="Intet link")
    
    if st.form_submit_button("Gem overnatningssted og send til Google Sheet"):
        if navn and hvem_er_du:
            beregnet_pris_pr_nat = int(total_regning / 4 / naetter) if (4 * naetter) > 0 else 0
            
            try:
                conn = connect(":memory:")
                cursor = conn.cursor()
                
                insert_query = f"""
                INSERT INTO "{GOOGLE_SHEET_URL}" 
                (id, Område, Navn, Lokation, "Pris pr. nat", Rating, Navn_Bruger, Kommentar, Link) 
                VALUES ('{len(hoteller_liste)+1}', '{aktuelt_omraade}', '{navn}', '{lokation}', {beregnet_pris_pr_nat}, {rating_valg}, '{hvem_er_du}', '{kommentar}', '{booking_link}')
                """
                cursor.execute(insert_query)
                st.success(f"🎉 {navn} blev gemt direkte i Google Sheet!")
                st.rerun()
            except Exception as e:
                st.error(f"Kunne ikke gemme i Google Sheet: {e}")
        else:
            st.error("Udfyld venligst både dit navn og hotellets navn!")

st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")

# Her er linje 104 rettet fuldstændigt:
filtreret_liste = [h for h in hoteller_liste if str(h.get("Område")) == aktuelt_omraade]

if not filtreret_liste:
    st.info("Ingen hoteller fundet i dette område endnu.")
else:
    tabel_data = []
    for h in filtreret_liste:
        try:
            pris_nat = float(h.get("Pris pr. nat", 0))
            rating_int = int(float(h.get("Rating", 5)))
        except:
            pris_nat =
