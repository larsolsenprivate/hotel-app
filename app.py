import streamlit as st
import pandas as pd
import re
import urllib.parse

st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

# ==============================================================================
# ⚠️ INDSÆT DIT GOOGLE SHEET LINK HERUNDER:
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/DIT_UNIKKE_ID_HER/edit?usp=sharing"
# ==============================================================================

try:
    sheet_id = re.search(r"/d/([^/]+)", GOOGLE_SHEET_URL).group(1)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
except:
    st.error("Google Sheet URL'en er ikke gyldig på linje 10.")
    st.stop()

def hent_data():
    try:
        df = pd.read_csv(csv_url)
        df['id'] = df['id'].astype(str)
        return df.to_dict(orient="records")
    except:
        return []

if "hoteller" not in st.session_state:
    st.session_state.hoteller = hent_data()

st.title("🇫🇷 Fælles Hoteljagt 2026")
st.subheader("Krav: 4 værelser (8 personer) | Max 1.000 kr. pr. person totalt")

fane = st.radio("Vælg område:", ["🍇 Alsace (2 nætter)", "🏔️ Alperne (6 nætter)"])
naetter = 2 if "Alsace" in fane else 6
aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

st.write("---")
booking_link = st.text_input("Indsæt Booking.com / Airbnb link her:")
automatisk_navn = ""
if booking_link and "booking.com" in booking_link:
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        automatisk_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt hotelnavn: {automatisk_navn}")

st.write("---")
st.subheader("Tilføj nyt sted")

with st.form("nyt_hotel_form", clear_on_submit=True):
    hvem_er_du = st.text_input("Dit navn:", placeholder="Christian")
    navn = st.text_input("Hotel / Airbnb Navn:", value=automatisk_navn)
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    total_regning = st.number_input(f"Samlet pris (For 4 værelser i alle {naetter} nætter i alt):", min_value=0, value=8000)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar:")
    
    if st.form_submit_button("Gem overnatningssted"):
        if navn and hvem_er_du:
            beregnet_pris_pr_nat = int(total_regning / 4 / naetter) if (4 * naetter) > 0 else 0
            nyt_hotel = {
                "id": str(len(st.session_state.hoteller) + 1),
                "Område": aktuelt_omraade,
                "Navn": navn,
                "Lokation": lokation,
                "Pris pr. nat": beregnet_pris_pr_nat,
                "Rating": int(rating_valg),
                "Navn_Bruger": hvem_er_du,
                "Kommentar": kommentar,
                "Link": booking_link if booking_link else "Intet link"
            }
            st.session_state.hoteller.append(nyt_hotel)
            st.rerun()
        else:
            st.error("Udfyld navn og hotelnavn!")

st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")
filtreret_liste = [h for h in st.session_state.hoteller if h["Område"] == aktuelt_omraade]
filtreret_liste = sorted(filtreret_liste, key=lambda x: x["Rating"], reverse=True)

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu.")
else:
    tabel_data = []
    for h in filtreret_liste:
        p_pers = int((h["Pris pr. nat"] / 2) * naetter)
        t_grup = int(h["Pris pr. nat"] * 4 * naetter)
        tabel_data.append({
            "Rating": "X" * int(h["Rating"]),
            "Navn": h["Navn"],
            "By": h["Lokation"],
            "Pris/Nat Værelse": f"{h['Pris pr. nat']} kr.",
            "Pris/Pers Total": f"{p_pers} kr.",
            "Total Gruppe (8 pers)": f"{t_grup} kr.",
            "Budget": "OK" if p_pers <= 1000 else "OVER",
            "Fundet af": h["Navn_Bruger"]
        })
    st.dataframe(pd.DataFrame(tabel_data), use_container_width=True, hide_index=True)

    for h in filtreret_liste:
        p_pers = int((h["Pris pr. nat"] / 2) * naetter)
        t_grup = int(h["Pris pr. nat"] * 4 * naetter)
        
        # Her er den fejlsikrede linje uden de slemme skråstreger:
        soege_streng = h["Navn"] + " " + h["Lokation"] + " France"
        maps_link = f
