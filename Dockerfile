# Vi bruger samme image til både API og frontend.
# docker-compose bestemmer hvilken fil der køres.
FROM python:3.13-slim

# Hent uv ind i containeren
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies først (så Docker kan cache dem)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Kopier resten af koden ind
COPY . .

# Få uv's venv ind i PATH
ENV PATH="/app/.venv/bin:$PATH"
