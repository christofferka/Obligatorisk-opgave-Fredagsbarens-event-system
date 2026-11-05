# Fredagsbarens event-system

En lille Flask API og en Streamlit-frontend til at holde styr på events og tilmeldinger i fredagsbaren.

## Kør det med Docker

Fra roden af projektet:

```bash
docker compose up --build
```

Så kører:

- **Frontenden** på http://localhost:8501
- **API'en** på http://localhost:5000 (så du kan teste den i Postman)

Stop det igen med Ctrl+C, og ryd op med `docker compose down`.

## Kør det lokalt uden Docker

Du skal have [uv](https://docs.astral.sh/uv/) installeret.

Åbn to terminaler:

```bash
# terminal 1 — API'en
uv run api.py
```

```bash
# terminal 2 — frontenden
uv run streamlit run app.py
```

Åbn så http://localhost:8501.

## Filer

- `api.py` — Flask API
- `swagger.json` — dokumentation af API'en (åbn i https://editor.swagger.io/)
- `app.py` — Streamlit-frontend
- `Dockerfile` + `docker-compose.yml` — til at køre det hele i Docker
