FROM python:3.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    make \
    gettext \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dockerize
ENV DOCKERIZE_VERSION=v0.9.9
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz -O - | tar -C /usr/local/bin -xzv

# Create non-root user
RUN groupadd -r django && useradd -r -g django -u 1000 django

# Create directory structure
# We create /app/.venv specifically to store dependencies outside the /src volume mount
RUN mkdir -p /app/static /app/.venv /src/logs /src/media /home/django /scripts && \
    chown -R django:django /src /app /home/django /scripts

WORKDIR /src

# Install uv globally
RUN pip install --no-cache-dir uv

# Configure uv to use our dedicated venv path instead of system python
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
# Ensure binaries from our venv take precedence
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER django

# Copy dependencies first (cached layer)
COPY --chown=django:django src/pyproject.toml src/uv.lock /src/
# Sync dependencies into /app/.venv
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=django:django src/ /src/

# Scripts and config
COPY --chown=django:django docker/backend/*.sh /scripts/
RUN chmod +x /scripts/*.sh
COPY --chown=django:django docker/backend/.bashrc /home/django/.bashrc
