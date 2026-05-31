import streamlit as st
import pandas as pd
import re
import urllib.parse

# Sæt siden op
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

# ==============================================================================
# ⚠️ INDSÆT DIT GOOGLE SHEET LINK HERUNDER:
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/DIT_UNIKKE_ID_HER/edit?usp=sharing"
# ==============================================================================

# Konverter Google Sheet linket til et direkte CSV-download-link
try:
    sheet_id = re.search(r"/d/([^/]+)", GOOGLE_SHEET_URL).group(1)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
except:
    st.error("Google Sheet URL'en er ikke gyldig. Tjek formatet på linje 11.")
    st.stop()

# Funktion til at hente data fra Google Sheets
def hent_data():
    try:
        df = pd.read_csv(csv_url)
        df['id'] = df['id'].astype(str)
        return df.to_dict(orient="records")
    except:
        return []

# Hent data ind i appen
if "hoteller" not in st.session_state:
    st.session_state.hoteller = hent_data()
    if not st.session_state.hoteller:
        # Standard-forslag hvis arket er tomt
        st.session_state.hoteller = [
            {"id": "1", "Område": "Alsace", "Navn": "Hôtel De La Tour", "Lokation": "Ribeauvillé Center", "Pris pr. nat": 900, "Rating": 5, "Navn_Bruger": "Mads", "Kommentar": "Vintårn i den gamle bydel! Super autentisk.", "Link": "https://www.booking.com"},
            {"id": "2", "Område": "Alsace", "Navn": "Gîte l'Ancienne Poterie", "Lokation": "Ribeauvillé", "Pris pr. nat": 1100, "Rating": 4, "Navn_Bruger": "Mette", "Kommentar": "Rigtig lækker placering.", "Link": "https://www.airbnb.dk"},
            {"id": "3", "Område": "Alperne", "Navn": "Chalet Les Praz", "Lokation": "Chamonix", "Pris pr. nat": 320, "Rating": 4, "Navn_Bruger": "Sofie", "Kommentar": "Superbilligt alternativ tæt på liften.", "Link": "https://www.airbnb.dk"}
        ]

st.title("🇫🇷 Fælles Hoteljagt 2026")
st.subheader("Krav: 2 værelser (4 personer) | Max 1.000 kr. pr. person totalt")

# Vælg Område
fane = st.radio("Vælg område:", ["🍇 Alsace (2 nætter)", "🏔️ Alperne (6 nætter)"])
naetter = 2 if "Alsace" in fane else 6
aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# --- AUTOMATISK LINK-INDLÆSER ---
st.write("---")
st.subheader("Træk data fra link")
booking_link = st.text_input("Indsæt Booking.com / Airbnb link her:")

automatisk_navn = ""
if booking_link and "booking.com" in booking_link:
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        automatisk_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt hotelnavn: **{automatisk_navn}**")

# --- FORMULAR: TILFØJ NYT STED ---
st.write("---")
st.subheader("Tilføj nyt sted")

with st.form("nyt_hotel_form", clear_on_submit=True):
    hvem_er_du = st.text_input("Dit navn (Hvem finder det?):", placeholder="F.eks. Christian")
    navn = st.text_input("Hotel / Airbnb Navn:", value=automatisk_navn)
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    pris_pr_nat = st.number_input("Pris pr. nat pr. værelse (DKK):", min_value=0, value=800)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar om stedet:")
    
    indsendt = st.form_submit_button("Gem overnatningssted")
    if indsendt:
        if navn and hvem_er_du:
            nyt_hotel = {
                "id": str(len(st.session_state.hoteller) + 1),
                "Område": aktuelt_omraade,
                "Navn": navn,
                "Lokation": lokation,
                "Pris pr. nat": pris_pr_nat,
                "Rating": rating_valg,
                "Navn_Bruger": hvem_er_du,
                "Kommentar": kommentar,
                "Link": booking_link if booking_link else "Intet link"
            }
            st.session_state.hoteller.append(nyt_hotel)
            st.success(f"🎉 {navn} er tilføjet!")
            st.rerun()
        else:
            st.error("Udfyld venligst både dit navn og hotellets navn!")

# --- DATA-FORBEREDELSE TIL TABEL OG LISTE ---
st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")

filtreret_liste = [h for h in st.session_state.hoteller if h["Område"] == aktuelt_omraade]
filtreret_liste = sorted(filtreret_liste, key=lambda x: x["Rating"], reverse=True)

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu.")
else:
    # 1. GENERER COMPACT SAMMENLIGNINGSTABEL
    tabel_data = []
    for h in filtreret_liste:
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 2 * naetter) # Ganger nu med 2 værelser i stedet for 4
        budget_status = "🟩 OK" if pris_pr_person_total <= 1000 else "🟥 OVER"
        
        tabel_data.append({
            "Rating": "⭐" * int(h["Rating"]),
            "Navn": h["Navn"],
            "By": h["Lokation"],
            "Pris/Nat Værelse": f"{h['Pris pr. nat']} kr.",
            "Pris/Pers Total": f"{pris_pr_person_total} kr.",
            "Total Gruppe (4 pers)": f"{total_gruppe_pris} kr.",
            "Budget": budget_status,
            "Fundet af": h["Navn_Bruger"]
        })
    
    # Vis tabellen i Streamlit
    df_visning = pd.DataFrame(tabel_data)
    st.dataframe(df_visning, use_container_width=True, hide_index=True)

    # 2. DETALJERET LISTE MED FOLD UD/IND (EXPANDERS)
    st.write("### 🔍 Klik på et hotel for detaljer og redigering")
    
    for h in filtreret_liste:
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 2 * naetter) # Ganger nu med 2 værelser i stedet for 4
        stjerner = "⭐" * int(h["Rating"])
        budget_ikon = "🟩" if pris_pr_person_total <= 1000 else "🟥"
        
        # Opret Google Maps søgelink automatisk baseret på navn og lokation
        soge_tekst = f"{h['Navn']} {h['Lokation']} France"
