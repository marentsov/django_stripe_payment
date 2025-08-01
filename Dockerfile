FROM python:3.13.2-slim

RUN apt-get update && apt-get install -yq make \
    && pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY . .

CMD ["sh", "-c", "make migrate && make prod-run"]