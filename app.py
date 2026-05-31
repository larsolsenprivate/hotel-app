import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

# DETTE ER REGLEN FOR DIN FORBINDELSE
# (Husk at jeres Google Sheet skal være åbent for redigering for alle med linket!)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1iiA6QHwivaP202J4mdNjV7uXhGjGqUNHSP5E0ahhb00/edit?gid=0#gid=0"

# Opret forbindelse til Google Sheets via Streamlit
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Hent eksisterende data
    df_eksisterende = conn.read(spreadsheet=GOOGLE_SHEET_URL, ttl=0)
    hoteller_liste = df_eksisterende.to_dict(orient="records")
except Exception as e:
    st.error("Kunne ikke forbinde til Google Sheet. Sørg for at linket er rigtigt, og at arket er sat til 'Alle med linket kan redigere'.")
    hoteller_liste = []

st.title("🇫🇷 Fælles Hoteljagt 2026")
st.subheader("Krav: 4 værelser (8 personer) | Max 1.000 kr. pr. person totalt")

fane = st.radio("Vælg område:", ["🍇 Alsace (2 nætter)", "🏔️ Alperne (6 nætter)"])
naetter = 2 if "Alsace" in fane else 6
aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"

st.write("---")
st.subheader("Tilføj nyt sted")

with st.form("nyt_hotel_form", clear_on_submit=True):
    hvem_er_du = st.text_input("Dit navn:", placeholder="Christian")
    navn = st.text_input("Hotel / Airbnb Navn:")
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    total_regning = st.number_input(f"Samlet pris (For 4 værelser i alle {naetter} nætter i alt):", min_value=0, value=8000)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem overnatningssted og synkroniser"):
        if navn and hvem_er_du:
            beregnet_pris_pr_nat = int(total_regning / 4 / naetter) if (4 * naetter) > 0 else 0
            
            # Lav den nye række som data
            ny_raekke = pd.DataFrame([{
                "id": str(len(hoteller_liste) + 1),
                "Område": aktuelt_omraade,
                "Navn": navn,
                "Lokation": lokation,
                "Pris pr. nat": beregnet_pris_pr_nat,
                "Rating": int(rating_valg),
                "Navn_Bruger": hvem_er_du,
                "Kommentar": kommentar,
                "Link": "Intet link"
            }])
            
            # Læg det sammen med det gamle og gem direkte i Google Sheets!
            df_opdateret = pd.concat([df_eksisterende, ny_raekke], ignore_index=True)
            conn.update(spreadsheet=GOOGLE_SHEET_URL, data=df_opdateret)
            
            st.success(f"🎉 {navn} er gemt DIREKTE i Google Sheets!")
            st.rerun()
        else:
            st.error("Udfyld navn og hotelnavn!")

st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")
filtreret_liste = [h for h in hoteller_liste if h.get("Område") == aktuelt_omraade]
filtreret_liste = sorted(filtreret_liste, key=lambda x: x.get("Rating", 0), reverse=True)

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu.")
else:
    tabel_data = []
    for h in filtreret_liste:
        p_pers = int((h.get("Pris pr. nat", 0) / 2) * naetter)
        t_grup = int(h.get("Pris pr. nat", 0) * 4 * naetter)
        tabel_data.append({
            "Rating": "X" * int(h.get("Rating", 5)),
            "Navn": h.get("Navn"),
            "By": h.get("Lokation"),
            "Pris/Pers Total": f"{p_pers} kr.",
            "Total Gruppe (8 pers)": f"{t_grup} kr.",
            "Budget": "OK" if p_pers <= 1000 else "OVER",
            "Fundet af": h.get("Navn_Bruger")
        })
    st.dataframe(pd.DataFrame(tabel_data), use_container_width=True, hide_index=True)

    for h in filtreret_liste:
        p_pers = int((h.get("Pris pr. nat", 0) / 2) * naetter)
        t_grup = int(h.get("Pris pr. nat", 0) * 4 * naetter)
        soege_streng = str(h.get("Navn")) + " " + str(h.get("Lokation")) + " France"
        maps_link = f"http://maps.google.com/?q={urllib.parse.quote(soege_streng)}"
        
        with st.expander(f"{h.get('Navn')} - {p_pers} kr./pers."):
            st.write(f"Fundet af: {h.get('Navn_Bruger')} | By: {h.get('Lokation')}")
            c_a, c_b = st.columns(2)
            c_a.write(f"📊 Pris pr. person: {p_pers} kr.")
            c_b.write(f"👥 Totalpris gruppe (8 pers): {t_grup} kr.")
            if p_pers <= 1000:
                c_b.success("Inden for budget!")
            else:
                c_b.error("Over budget!")
            
            if h.get("Kommentar"):
                st.info(f"Kommentar: {h.get('Kommentar')}")
            st.markdown(f"[📍 Vis på Google Maps]({maps_link})")

st.write("---")
st.markdown(f"[📊 Åbn det fælles Google Sheet]({GOOGLE_SHEET_URL})")
