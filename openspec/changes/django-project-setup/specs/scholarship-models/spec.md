## ADDED Requirements

### Requirement: User model
The `scholarships` app SHALL define a `User` model with student profile fields.

#### Scenario: User model has expected fields
- **WHEN** the `User` model is inspected
- **THEN** it SHALL have fields for `name`, `email`, `education`, `discipline`, and `prefecture`

#### Scenario: User model has __str__
- **WHEN** the `User` model is inspected
- **THEN** it SHALL implement `__str__()` returning the user's name

### Requirement: Scholarship model
The `scholarships` app SHALL define a `Scholarship` model with listing details.

#### Scenario: Scholarship model has expected fields
- **WHEN** the `Scholarship` model is inspected
- **THEN** it SHALL have fields for `name`, `provider`, `award_amount`, `education_level`, `discipline`, `prefecture`, `deadline`, `requirements`, and `description`

#### Scenario: Scholarship model has __str__
- **WHEN** the `Scholarship` model is inspected
- **THEN** it SHALL implement `__str__()` returning the scholarship name

### Requirement: ScholarshipRequest model
The `scholarships` app SHALL define a `ScholarshipRequest` model for user-submitted requests not yet listed.

#### Scenario: ScholarshipRequest model has expected fields
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** it SHALL have fields for `user` (ForeignKey to User), `scholarship_name`, `provider`, `award_amount`, and `notes`

#### Scenario: ScholarshipRequest model has __str__
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** it SHALL implement `__str__()` returning a human-readable description including the scholarship name
