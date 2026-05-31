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
    st.error("Google Sheet URL'en er ikke gyldig. Tjek formatet på linje 12.")
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

st.title("🇫🇷 Fælles Hoteljagt 2026")
st.subheader("Krav: 4 værelser (8 personer) | Max 1.000 kr. pr. person totalt")

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
        st.success(f"🤖 Fandt hotelnavn: {automatisk_navn}")

# --- FORMULAR: TILFØJ NYT STED ---
st.write("---")
st.subheader("Tilføj nyt sted")

with st.form("nyt_hotel_form", clear_on_submit=True):
    hvem_er_du = st.text_input("Dit navn (Hvem finder det?):", placeholder="F.eks. Christian")
    navn = st.text_input("Hotel / Airbnb Navn:", value=automatisk_navn)
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    
    total_regning = st.number_input(f"Samlet pris på regningen (For 4 værelser i alle {naetter} nætter i alt):", min_value=0, value=8000)
    
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar = st.text_area("Kommentar om stedet:")
    
    indsendt = st.form_submit_button("Gem overnatningssted")
    if indsendt:
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
            st.success(f"🎉 Tilføjet!")
            st.rerun()
        else:
            st.error("Udfyld venligst både dit navn og hotellets navn!")

# --- DATA-FORBEREDELSE TIL TABEL OG LISTE ---
st.write("---")
st.subheader(f"Muligheder i {aktuelt_omraade}")

filtreret_liste = [h for h in st.session_state.hoteller if h["Område"] == aktuelt_omraade]
filtreret_liste = sorted(filtreret_liste, key=lambda x: x["Rating"], reverse=True)

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu. Begynd at taste dem ind ovenfor!")
else:
    # 1. GENERER COMPACT SAMMENLIGNINGSTABEL
    tabel_data = []
    for h in filtreret_liste:
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 4 * naetter)
        budget_status = "OK" if pris_pr_person_total <= 1000 else "OVER"
        antil_stjerner = "X" * int(h["Rating"])
        
        tabel_data.append({
            "Rating": antil_stjerner,
            "Navn": h["Navn"],
            "By": h["Lokation"],
            "Pris/Nat Værelse": f"{h['Pris pr. nat']} kr.",
            "Pris/Pers Total": f"{pris_pr_person_total} kr.",
            "Total Gruppe (8 pers)": f"{total_gruppe_pris} kr.",
            "Budget": budget_status,
            "Fundet af": h["Navn_Bruger"]
        })
    
    df_visning = pd.DataFrame(tabel_data)
    st.dataframe(df_visning, use_container_width=True, hide_index=True)

    # 2. DETALJERET LISTE MED FOLD UD/IND (EXPANDERS)
    st.write("### 🔍 Klik på et hotel for detaljer og redigering")
    
    for h in filtreret_liste:
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 4 * naetter)
        
        soge_tekst = f"{h['Navn']} {h['Lokation']} France"
        maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(soge_tekst)}"
        
        titel_boks = f"{h['Navn']} - {pris_pr_person_total} kr./pers."
        
        with st.expander(titel_boks):
            st.write(f"Tilføjet af: {h['Navn_Bruger']} | Lokation: {h['Lokation']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"Pris pr. nat (1 værelse): {h['Pris pr. nat']} kr.")
                st.write(f"Pris pr. person ({naetter} nætter): {pris_pr_person_total} kr.")
            with col_b:
                st.write(f"Totalpris for gruppen (4 værelser): {total_gruppe_pris} kr.")
                if pris_pr_person_total <= 1000:
                    st.success("Inden for budget!")
                else:
                    st.error("Over budget!")
            
            if h["Kommentar"]:
                st.info(f"Kommentar: {h['Kommentar']}")
                
            link_col1, link_col2 = st.columns(2)
            with link_col1:
                if h["Link"] != "Intet link":
                    st.markdown(f"[🔗 Åbn hos Booking/Airbnb]({h['Link']})")
            with link_col2:
                st.markdown(f"[📍 Vis på Google Maps]({maps_link})")
            
            st.write("") 
            
            # Forenklet linje 164 her for at undgå fejl under kopiering
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📝 Rediger", key=f"edit_btn_{h['id']}"):
                    st.session_state.edit_id = h["id"]
                    st.rerun()
            with c2:
                if st.button("🗑️ Slet", key=f"del_btn_{h['id']}"):
                    st.session_state.hoteller = [x for x in st.session_state.hoteller if x["id"] != h["id"]]
                    st.rerun()
            
            if st.session_state.edit_id == h["id"]:
                st.markdown("---")
                st.markdown("#### Rediger oplysninger")
                with st.form(f"edit_form_{h['id']}"):
                    ny_rating = st.slider("Ændr rating:", 1, 5, value=int(h["Rating"]))
                    ny_kommentar = st.text_area("Ret kommentar:", value=h["Kommentar"])
                    
                    aktuel_total = int(h["Pris pr. nat"] * 4 * naetter)
                    ny_total = st.number_input("Ret totalpris for hele gruppen:", min_value=0, value=aktuel_total)
                    ny_by = st.text_input("Ret lokation:", value=h["Lokation"])
                    
                    if st.form_submit_button("Gem ændringer"):
                        for hotel in st.session_state.hoteller:
                            if hotel["id"] == h["id"]:
                                hotel["Rating"] = ny_rating
                                hotel["Kommentar"] = ny_kommentar
                                hotel["Pris pr. nat"] = int(ny_total / 4 / naetter) if (4 * naetter) > 0 else 0
                                hotel["Lokation"] = ny_by
                        st.session_state.edit_id = None
                        st.
