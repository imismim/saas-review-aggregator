FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/prod.txt

COPY . /app/

RUN mkdir -p /app/staticfiles

# create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["sh", "-c", "gunicorn --chdir src reviewaggregator.wsgi:application --bind 0.0.0.0:$PORT"]