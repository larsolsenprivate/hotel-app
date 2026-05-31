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
# 🔗 JERS RIGTIGE GOOGLE SHEET LINK (SAT IND AUTOMATISK):
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit?usp=sharing"
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
            st.rerun()
        else:
            st.error("Forkert adgangskode.")
    st.stop()

try:
    sheet_id = "1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
except:
    st.error("Google Sheet URL'en er ikke gyldig.")
    st.stop()

def hent_data():
    try:
        df = pd.read_csv(csv_url)
        return df.dropna(how="all").to_dict(orient="records")
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

booking_link = st.text_input("Indsæt link (Booking.com / Airbnb) HER FØRST for at hente navn automatisk:")

automatisk_navn = ""
if booking_link and "booking.com" in booking_link:
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        automatisk_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt automatisk hotelnavn: {automatisk_navn}")

with st.form("nyt_hotel_form", clear_on_submit=True):
    navne_liste = ["Lars", "Lotte", "Maja", "Mikkel", "Caroline", "Jørgen", "Charlotte", "Mads"]
    hvem_er_du = st.selectbox("Hvem finder det?", options=navne_liste)
    
    navn = st.text_input("Hotel / Airbnb Navn:", value=automatisk_navn)
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    total_regning = st.number_input(f"Samlet pris (For alle 4 værelser i alle {naetter} nætter i alt):", min_value=0, value=12000)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem overnatningssted og send til Google Sheet"):
        if navn and hvem_er_du:
            beregnet_pris_pr_nat = int(total_regning / 4 / naetter) if (4 * naetter) > 0 else 0
            gemt_link = booking_link if booking_link else "Intet link"
            try:
                conn = connect(":memory:")
                cursor = conn.cursor()
                insert_query = f"""
                INSERT INTO "{GOOGLE_SHEET_URL}" 
                (id, Område, Navn, Lokation, "Pris pr. nat", Rating, Navn_Bruger, Kommentar, Link) 
                VALUES ('{len(hoteller_liste)+1}', '{aktuelt_omraade}', '{navn}', '{lokation}', {beregnet_pris_pr_nat}, {rating_valg}, '{hvem_er_du}', '{kommentar}', '{gemt_link}')
                """
                cursor.execute(insert_query)
                st.success(f"🎉 Gemt!")
                st.rerun()
            except Exception as e:
                st.error(f"Fejl ved gem i Google Sheet: {e}")
        else:
            st.error("Udfyld navn!")

st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")
filtreret = [h for h in hoteller_liste if str(h.get("Område")) == aktuelt_omraade]

if not filtreret:
    st.info("Ingen hoteller fundet endnu.")
else:
    tabel_data = []
    for h in filtreret:
        try:
            # Vi bruger .get() med en backup-værdi for at undgå fejl hvis arket er tomt
            pris_n = float(h.get("Pris pr. nat", 0))
            rat_i = int(float(h.get("Rating", 5)))
        except:
            pris_n, rat_i = 0, 5
            
        p_pers = int((pris_n / 2) * naetter)
        t_grup = int(pris_n * 4 * naetter)
        
        tabel_data.append({
            "Rating": "X" * rat_i,
            "Navn": h.get("Navn"),
            "By": h.get("Lokation"),
            "Pris/Pers Total": f"{p_pers} kr.",
            "Total Gruppe (8 pers)": f"{t_grup} kr.",
            "Budget": "OK" if p_pers <= 1000 else "OVER",
            "Fundet af": h.get("Navn_Bruger")
        })
    st.dataframe(pd.DataFrame(tabel_data), use_container_width=True, hide_index=True)

st.write("---")
st.markdown(f"[📊 Åbn det fælles Google Sheet]({GOOGLE_SHEET_URL})")
