FROM python:3.11-slim-buster


ENV PYTHONDONTWRITEBYTECODE 1

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.6.1

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
  build-essential \
  gettext \
  libpq-dev \
  wget && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["sh", "-c", "python3 src/orders/__init__.py"]
