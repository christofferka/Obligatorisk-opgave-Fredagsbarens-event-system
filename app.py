import os
import httpx
import pandas as pd
import streamlit as st

# API'en ligger forskellige steder lokalt og i Docker, så vi læser adressen fra en env-var
API_URL = os.environ.get("API_URL", "http://localhost:5000")

# Kort timeout så vi mærker det hvis API'en hænger
TIMEOUT = 2


st.set_page_config(page_title="Fredagsbaren", page_icon="🍻")
st.title("Fredagsbarens event-system")


# Husk brugerens navn på tværs af klik
if "name" not in st.session_state:
    st.session_state.name = ""

st.sidebar.header("Mit navn")
st.session_state.name = st.sidebar.text_input(
    "Hvad hedder du?", value=st.session_state.name
)


def hent_events():
    """Henter alle events. Returnerer None hvis noget går galt (og viser en fejl)."""
    try:
        r = httpx.get(f"{API_URL}/events", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("Kunne ikke få fat på API'en. Er den startet?")
    except httpx.TimeoutException:
        st.error("API'en svarer for langsomt.")
    except httpx.HTTPStatusError as e:
        # Hvis API'en sendte en pæn fejlbesked, vis den
        besked = e.response.json().get("error", "Ukendt fejl")
        st.error(f"Fejl fra API: {besked}")
    return None


events = hent_events()
if events is None:
    st.stop()


# ----- Oversigt -----
st.header("Kommende events")

# Vi laver en lille tabel med det der er rart at se
rows = []
for e in events:
    rows.append({
        "Titel": e["title"],
        "Dato": e["date"],
        "Tilmeldte": len(e["participants"]),
        "Ledige pladser": e["capacity"] - len(e["participants"]),
    })

st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


# ----- Tilmeld / afmeld -----
st.header("Tilmeld eller afmeld")

valgt_titel = st.selectbox(
    "Vælg event",
    options=[e["title"] for e in events],
)
valgt = next(e for e in events if e["title"] == valgt_titel)

st.write(f"**Dato:** {valgt['date']}")
st.write(f"**Deltagere:** {', '.join(valgt['participants']) if valgt['participants'] else 'ingen endnu'}")
st.write(f"**Ledige pladser:** {valgt['capacity'] - len(valgt['participants'])}")

fuldt = len(valgt["participants"]) >= valgt["capacity"]
navn = st.session_state.name.strip()

col1, col2 = st.columns(2)

with col1:
    if st.button("Tilmeld mig", disabled=fuldt or not navn):
        try:
            r = httpx.post(
                f"{API_URL}/events/{valgt['id']}/signups",
                json={"name": navn},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            st.success(f"{navn} er tilmeldt!")
            st.rerun()
        except httpx.ConnectError:
            st.error("Kunne ikke få fat på API'en.")
        except httpx.TimeoutException:
            st.error("API'en svarer for langsomt.")
        except httpx.HTTPStatusError as e:
            besked = e.response.json().get("error", "Ukendt fejl")
            st.error(f"Det gik galt: {besked}")

with col2:
    if st.button("Afmeld mig", disabled=not navn):
        try:
            r = httpx.delete(
                f"{API_URL}/events/{valgt['id']}/signups/{navn}",
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            st.success(f"{navn} er afmeldt.")
            st.rerun()
        except httpx.ConnectError:
            st.error("Kunne ikke få fat på API'en.")
        except httpx.TimeoutException:
            st.error("API'en svarer for langsomt.")
        except httpx.HTTPStatusError as e:
            besked = e.response.json().get("error", "Ukendt fejl")
            st.error(f"Det gik galt: {besked}")

if fuldt:
    st.info("Eventet er fuldt — tilmelding er deaktiveret.")
if not navn:
    st.info("Skriv dit navn i sidebar for at kunne tilmelde dig.")


# ----- Opret nyt event -----
st.header("Opret nyt event")

with st.form("nyt_event"):
    titel = st.text_input("Titel")
    dato = st.date_input("Dato")
    pladser = st.number_input("Antal pladser", min_value=1, value=10, step=1)
    opret = st.form_submit_button("Opret")

    if opret:
        try:
            r = httpx.post(
                f"{API_URL}/events",
                json={
                    "title": titel,
                    "date": dato.isoformat(),
                    "capacity": int(pladser),
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            st.success(f"Event '{titel}' er oprettet!")
            st.rerun()
        except httpx.ConnectError:
            st.error("Kunne ikke få fat på API'en.")
        except httpx.TimeoutException:
            st.error("API'en svarer for langsomt.")
        except httpx.HTTPStatusError as e:
            besked = e.response.json().get("error", "Ukendt fejl")
            st.error(f"Kunne ikke oprette event: {besked}")
