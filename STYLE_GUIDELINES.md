# Project Style Guidelines

## 1. Technology Stack
- **Language:** Python 3.14
- **Framework:** Django 6.0
- **API:** Django Rest Framework (DRF)
- **Async/Tasks:** Celery + RabbitMQ
- **Package Manager:** `uv`

## 2. Code Formatting & Quality
We enforce strict code quality rules via `pre-commit` hooks. You must run `pre-commit install` locally.

### Formatters
- **Black:** Line length 88.
- **Isort:** Profile compatible with Black.
- **Ruff:** For linting and fast static analysis.

### Rules
- **Type Hinting:** Required for all function arguments and return types. Checked via `mypy`.
- **Strings:** Double quotes `"` are preferred over single quotes `'` for string literals (enforced by Black), except when avoiding escaping.
- **Comments:** Do not leave commented-out code. Comments should be in English and used sparingly only for complex logic.

## 3. Project Structure
We follow a Domain-Driven Design (DDD) inspired structure located in `src/apps/`.

```text
src/apps/<app_name>/
├── admin/          # Django Admin configuration
├── api/            # DRF Views, Serializers, URLs, Permissions
├── models/         # Database models and Managers
├── tasks/          # Celery tasks
├── services/       # Business logic (optional)
└── tests/          # App-specific tests

```

### Django Conventions

* **Models:** Inherit from `TimeStampedUUIDModel` (in `core.models.abstract`) unless there is a strong reason not to.
* **Users:** Use the custom `User` model in `core`.
* **Settings:** Managed via `django-environ`. Do not hardcode secrets.

## 4. Internationalization (i18n)

All user-facing strings **must** be marked for translation.

* **Import:** `from django.utils.translation import gettext_lazy as _`
* **Usage:** `name = models.CharField(verbose_name=_("Name"), ...)`

## 5. Testing

* **Framework:** `django.test.TestCase` or `APITestCase`.
* **Data:** Use `factory_boy` factories (located in `apps/<app>/factories/`). **Do not use Fixtures.**
* **Coverage:** Minimum 90% coverage is required (configured in `pyproject.toml`).

## 6. Git Workflow & Branching

* **Main Branch:** `main` (Protected).
* **Branch Naming:**
* Features: `feature/ticket-description`
* Fixes: `fix/ticket-description`
* Chores: `chore/ticket-description`

## 7. Dependency Management

* Add dependencies using `uv add <package>`.
* Lock files (`uv.lock`) must be committed.
