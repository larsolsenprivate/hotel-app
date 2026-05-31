import streamlit as st
import pandas as pd
import re

# Sæt siden op
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

st.title("🇫🇷 Hoteljagt - Gruppe på 8 personer")
st.subheader("Krav: 4 værelser | Max 1.000 kr. pr. person for hele opholdet")

# 1. Vælg Område (Faneblade i Streamlit)
fane = st.radio("Vælg område:", ["🍇 Alsace (17.-19. juli - 2 nætter)", "🏔️ Alperne (19.-25. juli - 6 nætter)"])
naetter = 2 if "Alsace" in fane else 6

# Session state til at gemme hoteller (virker som appens hukommelse)
if "hoteller" not in st.session_state:
    st.session_state.hoteller = []

# --- AUTOMATISK LINK-INDLÆSER ---
st.write("---")
st.subheader("Træk data automatisk fra link")
booking_link = st.text_input("Indsæt Booking.com link her:")

automatisk_navn = ""
if booking_link:
    # Simpel "Scraper" logik: Vi tager hotelnavnet ud fra selve URL-teksten
    # Da Booking.coms links ofte indeholder hotelnavnet i teksten (f.eks. /hotel/fr/alpina-chamonix.html)
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        automatisk_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt automatisk hotelnavn: **{automatisk_navn}**")
    else:
        st.warning("Kunne ikke gætte navnet ud fra linket, men du kan skrive det manuelt nedenfor.")

# --- FORMULAR (MANUEL / OPDRATERET AF LINK) ---
st.write("---")
st.subheader("Tilføj eller ret oplysninger")

navn = st.text_input("Hotelnavn:", value=automatisk_navn)
lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
pris_pr_nat = st.number_input("Pris pr. nat pr. værelse (DKK):", min_value=0, value=800)
rating = st.slider("Din rating:", 1, 5, 5)
kommentar = st.text_area("Kommentar (f.eks. værelsestype, pool osv.):")

if st.button("Gem overnatningssted"):
    if navn:
        nyt_hotel = {
            "Område": "Alsace" if naetter == 2 else "Alperne",
            "Navn": navn,
            "Lokation": lokation,
            "Pris pr. nat": pris_pr_nat,
            "Rating": "⭐" * rating,
            "Kommentar": kommentar,
            "Link": booking_link if booking_link else "Intet link"
        }
        st.session_state.hoteller.append(nyt_hotel)
        st.balloons()
        st.success(f"{navn} er gemt!")
    else:
        st.error("Hotellet skal have et navn!")

# --- VISNING AF GEMTE HOTELLER & BUDGETTJEK ---
st.write("---")
st.subheader("Gemte muligheder")

aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"
filtreret_liste = [h for h in st.session_state.hoteller if h["Område"] == aktuelt_omraade]

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu.")
else:
    for h in filtreret_liste:
        # Budgetberegning
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 4 * naetter)
        
        with st.expander(f"{h['Rating']} {h['Navn']} - {h['Lokation']}"):
            st.write(f"💰 **Pris pr. nat (pr. værelse):** {h['Pris pr. nat']} kr.")
            st.write(f"👥 **Totalpris for hele gruppen (4 værelser, {naetter} nætter):** {total_gruppe_pris} kr.")
            
            # Budget-alarm
            if pris_pr_person_total <= 1000:
                st.success(f"🟩 Pris pr. person: {pris_pr_person_total} kr. (INDEN FOR BUDGET)")
            else:
                st.error(f"🟥 Pris pr. person: {pris_pr_person_total} kr. (OVER BUDGET MED {pris_pr_person_total - 1000} KR.)")
                
            if h["Kommentar"]:
                st.info(f"💬 **Kommentar:** {h['Kommentar']}")
            if h["Link"] != "Intet link":
                st.markdown(f"[🔗 Åbn linket på Booking.com]({h['Link']})")
