
# Ideological Atlas - Backend API

![CI](https://github.com/Ideological-Atlas/backend/actions/workflows/cicd.yml/badge.svg)
[![codecov](https://codecov.io/gh/Ideological-Atlas/backend/graph/badge.svg?token=W9D4BVTK2Y)](https://app.codecov.io/gh/Ideological-Atlas/backend)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Django](https://img.shields.io/badge/django-6.0-092E20?logo=django&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-blueviolet)](https://github.com/gitleaks/gitleaks)
[![shellcheck](https://img.shields.io/badge/shellcheck-enforced-4EAA25)](https://github.com/koalaman/shellcheck)
[![codespell](https://img.shields.io/badge/spell%20check-codespell-blue)](https://github.com/codespell-project/codespell)

## 📖 Description

This repository contains the **Backend API** for the *Ideological Atlas* project. It is a robust and scalable application designed to manage users, complex ideological test structures, affinity calculations, and geographic/ideological content management.

The system is built on a modern container-based architecture, utilizing the latest stable versions of its core technologies.

## 🛠️ Technology Stack

The infrastructure relies on the following main components:

* **Language:** Python 3.14
* **Web Framework:** Django 6.0
* **API:** Django Rest Framework (DRF) 3.16+
* **Database:** PostgreSQL 18
* **Package Manager:** uv
* **Async & Tasks:** Celery 5.6 + RabbitMQ 4
* **Storage:** MinIO (S3 Compatible)
* **Containerization:** Docker & Docker Compose

## 🚀 Installation and Local Deployment

The project is fully containerized to facilitate development. A `Makefile` is used to orchestrate the most common commands.

### Prerequisites

* Docker Engine
* Docker Compose
* Make (Optional, but recommended)

### Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ideological-Atlas/backend.git
    cd backend
    ```

2.  **Build and start the environment:**
    This command creates the network, generates the `.env` file from the template, builds the images, and starts the containers in the background.
    ```bash
    make build
    ```

3.  **Check status:**
    You can view real-time logs to ensure everything started correctly (Backend, Worker, Beat, Flower, Postgres, MinIO).
    ```bash
    make logs
    ```

The backend will be available at `http://localhost:3141` (or the port defined in your `.env`).

## ⚙️ Project Management (Makefile)

The `Makefile` is the main interface for interacting with the development environment.

| Command | Description |
| :--- | :--- |
| `make up` | Starts containers (forces recreation). |
| `make down` | Stops and removes containers and networks. |
| `make logs` | Shows logs for the backend container. |
| `make celery-logs` | Shows logs for Celery workers. |
| `make bash` | Opens a bash terminal inside the `backend` container. |
| `make shell` | Opens a Django shell (`shell_plus`) with iPython. |
| `make test` | Runs the full test suite with coverage. |
| `make migrations` | Creates and applies pending migrations. |
| `make messages` | Extracts and compiles translation messages (i18n). |
| `make clean-images` | Removes project Docker images. |

## 🧪 Code Quality & Testing

We maintain strict quality standards using `pre-commit` and several static analysis tools.

### Pre-commit
It is recommended to install the hooks locally to avoid CI failures:
```bash
uv tool install pre-commit
pre-commit install
```

### Running Tests

To run tests inside the Docker container and generate coverage reports:

```bash
make test
```

*The system requires a minimum coverage of 90% to pass CI.*

### Configured Tools

* **Ruff:** Fast linter and formatter.
* **Black & Isort:** Code formatting and import sorting.
* **Mypy:** Static type checking.
* **Bandit & Gitleaks:** Security analysis and secret detection.

## 📂 Project Structure

We follow a structure inspired by DDD (Domain-Driven Design) located in `src/apps/`.

```text
.
├── docker/                 # Docker configurations
├── src/
│   ├── apps/
│   │   ├── core/           # Users, Auth, Geo, Base utilities
│   │   └── ideology/       # Business logic: Tests, Axes, Affinity Calculation
│   ├── backend/            # Django project configuration (settings, urls)
│   ├── locale/             # Translation files
│   └── tests/              # Unit and integration tests
└── Makefile                # Command orchestration

```

## 📚 API Documentation

In the development environment (`PRODUCTION=False`), interactive documentation is available at:

* **Swagger UI:** `http://localhost:3141/api/schema/swagger-ui/`
* **ReDoc:** `http://localhost:3141/api/schema/redoc/`

## 🌍 Internationalization

The project supports multiple languages (Default: Spanish and English).
To update translations after modifying the code:

```bash
make messages
```

This will automatically execute `makemessages` and `compilemessages` for the `es` locale.

---

**Powered by [Django](https://www.djangoproject.com/)**
