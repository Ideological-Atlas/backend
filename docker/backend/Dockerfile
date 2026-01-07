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
RUN mkdir -p /app/static /src/logs /src/media /home/django /scripts && \
    chown -R django:django /src /app /home/django /scripts

WORKDIR /src

# Install uv globally
RUN pip install --no-cache-dir uv

# Install dependencies (system-wide)
COPY src/pyproject.toml src/uv.lock /src/

# Allow de dependencies dev if required
ARG INSTALL_DEV=FALSE
RUN if [ "$INSTALL_DEV" = "TRUE" ]; then \
        uv export --frozen --format requirements-txt --extra dev | uv pip install --system -r /dev/stdin; \
    else \
        uv export --frozen --no-dev --format requirements-txt | uv pip install --system -r /dev/stdin; \
    fi

# Switch to non-root user
USER django

# Copy application code
COPY --chown=django:django src/ /src/

# Scripts and config
COPY --chown=django:django docker/backend/*.sh /scripts/
RUN chmod +x /scripts/*.sh
COPY --chown=django:django docker/backend/.bashrc /home/django/.bashrc
