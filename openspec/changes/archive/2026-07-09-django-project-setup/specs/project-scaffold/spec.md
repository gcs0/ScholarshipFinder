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


