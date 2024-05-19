FROM python:3.11-buster as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# RUN --mount=type=cache,id=123,target=$POETRY_CACHE_DIR poetry install --no-root
RUN --mount=type=cache,id=s/12345-$POETRY_CACHE_DIR,target=$POETRY_CACHE_DIR poetry install --no-root
# RUN --mount=type=cache,id=s/f39fcb94-3436-4d82-9504-93147718bf98-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install poetry==1.3.1 && poetry install --no-dev --no-interaction --no-ansi

FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="${PYTHONPATH}:/app/bot"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "bot/main.py"]
