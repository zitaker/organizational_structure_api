# System Image
FROM python:3.13.0-slim

# Installing updates and necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*.bin

# Installing the working directory
WORKDIR /app

# Copying the dependency files
COPY pyproject.toml ./

# Installing dependencies
RUN pip install --upgrade pip \
    && pip install ".[test,dev]" \
    && rm -rf /root/.cache/pip

# Copying all project files
COPY . .

# Setting environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=src.conf.settings

# The default startup command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]