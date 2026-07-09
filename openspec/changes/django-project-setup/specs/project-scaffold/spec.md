## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Package skeleton
**Reason**: Replaced by Django project structure with `scholarships/` app at root.
**Migration**: Core entities are now defined as Django models in `scholarships/models.py` instead of stub modules under `src/scholarship_finder/`.

#### Scenario: Package directory exists
- **WHEN** the `src/` directory is inspected
- **THEN** a `src/scholarship_finder/` directory SHALL exist

#### Scenario: Package init exists
- **WHEN** `src/scholarship_finder/` is inspected
- **THEN** it SHALL contain an `__init__.py` file

#### Scenario: User module stub
- **WHEN** `src/scholarship_finder/` is inspected
- **THEN** it SHALL contain a `user.py` module

#### Scenario: Scholarship module stub
- **WHEN** `src/scholarship_finder/` is inspected
- **THEN** it SHALL contain a `scholarship.py` module

#### Scenario: Scholarship request module stub
- **WHEN** `src/scholarship_finder/` is inspected
- **THEN** it SHALL contain a `scholarship_request.py` module

### Requirement: Test scaffolding
**Reason**: Replaced by Django app's built-in `tests.py`.
**Migration**: Tests will live in `scholarships/tests.py` instead of a separate `tests/` directory.

#### Scenario: Tests directory exists
- **WHEN** the project is inspected
- **THEN** a `tests/` directory SHALL exist

#### Scenario: Placeholder test exists
- **WHEN** `tests/` is inspected
- **THEN** it SHALL contain at least one Python test file
