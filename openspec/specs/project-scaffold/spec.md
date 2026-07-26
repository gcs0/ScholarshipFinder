# project-scaffold Specification

## Purpose
TBD - created by archiving change initial-project-setup. Update Purpose after archive.
## Requirements
### Requirement: Python project configuration
The project SHALL include a `pyproject.toml` in the repository root defining project metadata and tooling configuration.

#### Scenario: pyproject.toml exists
- **WHEN** the project is inspected
- **THEN** a `pyproject.toml` file SHALL exist at the repository root

#### Scenario: Project metadata is defined
- **WHEN** `pyproject.toml` is parsed
- **THEN** it SHALL contain `[project]` with `name`, `version`, `description`, and `requires-python`

#### Scenario: Black is configured
- **WHEN** `pyproject.toml` is parsed
- **THEN** it SHALL contain a `[tool.black]` section

#### Scenario: Ruff is configured
- **WHEN** `pyproject.toml` is parsed
- **THEN** it SHALL contain a `[tool.ruff]` section

#### Scenario: pytest is configured
- **WHEN** `pyproject.toml` is parsed
- **THEN** it SHALL contain a `[tool.pytest.ini_options]` section

### Requirement: Repository ignores
The repository SHALL include a `.gitignore` file excluding Python bytecode, virtual environments, cache directories, and editor artifacts.

#### Scenario: .gitignore exists
- **WHEN** the project is inspected
- **THEN** a `.gitignore` file SHALL exist at the repository root

#### Scenario: Virtual environments are ignored
- **WHEN** `.gitignore` is parsed
- **THEN** it SHALL include an entry for `.venv/`

#### Scenario: Python cache files are ignored
- **WHEN** `.gitignore` is parsed
- **THEN** it SHALL include entries for `__pycache__/` and `*.pyc`

### Requirement: Package skeleton
The project SHALL contain a `scholarships/` Django app directory with `models.py` defining the three core entities as Django models.

#### Scenario: App directory exists
- **WHEN** the repository root is inspected
- **THEN** a `scholarships/` directory SHALL exist

#### Scenario: Models file exists
- **WHEN** `scholarships/` is inspected
- **THEN** it SHALL contain a `models.py` file

#### Scenario: User model defined
- **WHEN** `scholarships/models.py` is inspected
- **THEN** it SHALL define a `User` model class

#### Scenario: Scholarship model defined
- **WHEN** `scholarships/models.py` is inspected
- **THEN** it SHALL define a `Scholarship` model class

#### Scenario: ScholarshipRequest model defined
- **WHEN** `scholarships/models.py` is inspected
- **THEN** it SHALL define a `ScholarshipRequest` model class

### Requirement: Test scaffolding
The `scholarships` app SHALL include a `tests.py` file (created by `startapp`) with at least one test.

#### Scenario: Tests file exists
- **WHEN** `scholarships/` is inspected
- **THEN** it SHALL contain a `tests.py` file

#### Scenario: Import succeeds
- **WHEN** `python -c "from scholarships.models import User, Scholarship, ScholarshipRequest"` is run
- **THEN** it SHALL exit with code 0

### Requirement: Tooling commands pass
The project SHALL be configured so that `ruff check .` and `black --check .` pass, and Django system checks pass.

#### Scenario: Django system checks pass
- **WHEN** `python manage.py check` is run
- **THEN** it SHALL exit with code 0

