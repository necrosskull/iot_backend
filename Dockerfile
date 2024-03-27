FROM python:3.11.7-slim-bullseye AS python

# Poetry configuration
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create a project directory
WORKDIR /app

# Copy poetry.lock and pyproject.toml
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-root --no-interaction --no-ansi

# Copy the rest of the project
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]