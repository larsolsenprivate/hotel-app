# 1. TABEL SEKTION (Vises øverst)
st.subheader("📊 Oversigt over hoteller")

# Knap til at tvinge genindlæsning af data
if st.button("🔄 Opdatér data fra ark"):
    st.cache_data.clear()
    st.rerun()

st.link_button("✏️ Åbn Google Sheet for at rette/slette", SHEET_EDIT_URL)

try:
    # Vi bruger st.cache_data så den kun henter når du trykker på knappen eller siden loader
    @st.cache_data(ttl=600) # Opdaterer automatisk hvert 10. minut, eller ved knaptryk
    def hent_data(url):
        df = pd.read_csv(url)
        return df

    df = hent_data(csv_url)
    
    # Rens data for at undgå fejl
    df['Pris'] = pd.to_numeric(df['Pris'], errors='coerce')
    df = df.dropna(subset=['Navn'])
    
    # Vis tabel
    st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True)
except Exception:
    st.info("Ingen hoteller fundet endnu. Tilføj det første hotel nedenfor.")
