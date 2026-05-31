import streamlit as st
import re

# Sæt siden op
st.set_page_config(page_title="Hoteljagt Frankrig 2026", page_icon="🇫🇷", layout="centered")

st.title("🇫🇷 Hoteljagt - Gruppe på 8 personer")
st.subheader("Krav: 4 værelser | Max 1.000 kr. pr. person for hele opholdet")

# 1. Vælg Område (Faneblade)
fane = st.radio("Vælg område:", ["🍇 Alsace (17.-19. juli - 2 nætter)", "🏔️ Alperne (19.-25. juli - 6 nætter)"])
naetter = 2 if "Alsace" in fane else 6
aktuelt_omraade = "Alsace" if naetter == 2 else "Alperne"

# Session state til at gemme hoteller (appens hukommelse)
if "hoteller" not in st.session_state:
    # Standard-forslag lagt ind fra start
    st.session_state.hoteller = [
        {
            "id": "def_alsace_1", "Område": "Alsace", "Navn": "Hôtel De La Tour", "Lokation": "Ribeauvillé Center",
            "Pris pr. nat": 900, "Rating": 5, "CommentP1": "Ligger i et gammelt vintårn! Super autentisk.", "CommentP2": "Passer perfekt under budgettet.", "Link": "https://www.booking.com/hotel/fr/de-la-tour-ribeauville.html"
        },
        {
            "id": "def_alper_2", "Område": "Alperne", "Navn": "Chalet Les Praz Lejligheder", "Lokation": "Chamonix",
            "Pris pr. nat": 320, "Rating": 4, "CommentP1": "Meget billigere alternativ tæt på liften.", "CommentP2": "Her kan vi bo superbilligt i alle 6 dage.", "Link": "https://www.airbnb.dk"
        }
    ]

# Hukommelse til at styre, hvilket hotel der redigeres lige nu
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# --- AUTOMATISK LINK-INDLÆSER ---
st.write("---")
st.subheader("Træk data automatisk fra link")
booking_link = st.text_input("Indsæt Booking.com link her:")

automatisk_navn = ""
if booking_link:
    match = re.search(r'/hotel/[a-z]{2}/([^.]+)', booking_link)
    if match:
        automatisk_navn = match.group(1).replace("-", " ").title()
        st.success(f"🤖 Fandt automatisk hotelnavn: **{automatisk_navn}**")

# --- FORMULAR TIL AT TILFØJE NYT STED ---
st.write("---")
st.subheader("Tilføj nyt sted manuelt")

with st.form("nyt_hotel_form", clear_on_submit=True):
    navn = st.text_input("Hotelnavn:", value=automatisk_navn)
    lokation = st.text_input("By / Lokation:", value="Ribeauvillé" if naetter == 2 else "Chamonix")
    pris_pr_nat = st.number_input("Pris pr. nat pr. værelse (DKK):", min_value=0, value=800)
    rating_valg = st.slider("Din rating:", 1, 5, 5)
    kommentar1 = st.text_area("Kommentarer - Person 1:")
    kommentar2 = st.text_area("Kommentarer - Person 2:")
    
    indsendt = st.form_submit_button("Gem overnatningssted")
    if indsendt:
        if navn:
            nyt_hotel = {
                "id": 'hotel_' + str(st.session_state.hoteller.__len__() + 1),
                "Område": aktuelt_omraade,
                "Navn": navn,
                "Lokation": lokation,
                "Pris pr. nat": pris_pr_nat,
                "Rating": rating_valg,
                "CommentP1": kommentar1,
                "CommentP2": kommentar2,
                "Link": booking_link if booking_link else "Intet link"
            }
            st.session_state.hoteller.append(nyt_hotel)
            st.success(f"🎉 {navn} er tilføjet til listen!")
            st.rerun()
        else:
            st.error("Stedet skal have et navn!")

# --- VISNING OG REDIGERING AF GEMTE HOTELLER ---
st.write("---")
st.subheader("Gemte muligheder (Sorteret efter rating)")

filtreret_liste = [h for h in st.session_state.hoteller if h["Område"] == aktuelt_omraade]
# Sorter efter rating (højeste først)
filtreret_liste = sorted(filtreret_liste, key=lambda x: x["Rating"], reverse=True)

if not filtreret_liste:
    st.info("Ingen hoteller gemt i dette område endnu.")
else:
    for h in filtreret_liste:
        pris_pr_person_total = int((h["Pris pr. nat"] / 2) * naetter)
        total_gruppe_pris = int(h["Pris pr. nat"] * 4 * naetter)
        stjerner = "⭐" * h["Rating"]
        
        # Opret et pænt kort til hotellet
        with st.container(border=True):
            st.markdown(f"### {stjerner} {h['Navn']}")
            st.write(f"📍 **Lokation:** {h['Lokation']}")
            st.write(f"🛏️ **Pris pr. nat pr. værelse:** {h['Pris pr. nat']} kr.")
            st.write(f"👥 **Totalpris for gruppen (4 værelser, {naetter} nætter):** {total_gruppe_pris} kr.")
            
            # Budgettjek
            if pris_pr_person_total <= 1000:
                st.success(f"🟩 Pris pr. person for hele opholdet: {pris_pr_person_total} kr. (INDEN FOR BUDGET)")
            else:
                st.error(f"🟥 Pris pr. person for hele opholdet: {pris_pr_person_total} kr. (OVER BUDGET MED {pris_pr_person_total - 1000} KR.)")
                
            if h["CommentP1"]:
                st.info(f"💬 **Person 1:** {h['CommentP1']}")
            if h["CommentP2"]:
                st.info(f"💬 **Person 2:** {h['CommentP2']}")
                
            if h["Link"] != "Intet link":
                st.markdown(f"[🔗 Åbn linket på Booking/Airbnb]({h['Link']})")
            
            # To knapper i bunden af hvert hotel: Rediger og Slet
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📝 Rediger", key=f"edit_btn_{h['id']}"):
                    st.session_state.edit_id = h["id"]
                    st.rerun()
            with col2:
                if st.button("🗑️ Slet", key=f"del_btn_{h['id']}", type="secondary"):
                    st.session_state.hoteller = [x for x in st.session_state.hoteller if x["id"] != h["id"]]
                    st.rerun()
            
            # --- POP-UP REDIGERINGS-MENU HVIS MAN HAR KLIKKET PÅ 'REDIGER' ---
            if st.session_state.edit_id == h["id"]:
                st.markdown("#### ✏️ Rediger oplysninger")
                with st.form(f"edit_form_{h['id']}"):
                    ny_rating = st.slider("Ændr rating:", 1, 5, value=h["Rating"])
                    ny_p1 = st.text_area("Ret kommentar - Person 1:", value=h["CommentP1"])
                    ny_p2 = st.text_area("Ret kommentar - Person 2:", value=h["CommentP2"])
                    ny_pris = st.number_input("Ret pris pr. nat:", min_value=0, value=h["Pris pr. nat"])
                    
                    gem_col, annuller_col = st.columns(2)
                    with gem_col:
                        if st.form_submit_button("Gem ændringer"):
                            # Opdater dataen i vores session_state list
                            for hotel in st.session_state.hoteller:
                                if hotel["id"] == h["id"]:
                                    hotel["Rating"] = ny_rating
                                    hotel["CommentP1"] = ny_p1
                                    hotel["CommentP2"] = ny_p2
                                    hotel["Pris pr. nat"] = ny_pris
                            st.session_state.edit_id = None  # Luk menuen
                            st.rerun()
                    with annuller_col:
                        if st.form_submit_button("Annuller"):
                            st.session_state.edit_id = None  # Luk menuen uden at gemme
                            st.rerun()
