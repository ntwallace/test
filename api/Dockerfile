FROM python:3.11.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    # apt-get install -y libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1
ENV PATH="$PATH:$POETRY_HOME/bin:/root/.poetry/bin"

# Install python dependencies
WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry install --only main

# Copy project
COPY . /app

# Run entrypoint
CMD ["./docker-entrypoint.sh"]
