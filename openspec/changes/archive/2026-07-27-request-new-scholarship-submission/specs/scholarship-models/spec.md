# scholarship-models Delta Spec

## MODIFIED Requirements

### Requirement: ScholarshipRequest model
The `scholarships` app SHALL define a `ScholarshipRequest` model for user-submitted requests describing a scholarship that is not yet listed in the system. The model SHALL NOT reference an existing `Scholarship` row as the subject of the request.

#### Scenario: ScholarshipRequest model has expected fields
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** it SHALL have fields for `user` (ForeignKey to `User`), `scholarship_name`, `provider`, `award_amount`, `notes`, `status`, `admin_notes`, `reviewed_by` (nullable ForeignKey to `User`), and `reviewed_date`

#### Scenario: ScholarshipRequest model has no scholarship foreign key
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** it SHALL NOT define a foreign key to `Scholarship` as the subject of the request
- **AND** it MAY define a nullable `created_scholarship` foreign key used only to record the `Scholarship` row produced on approval

#### Scenario: ScholarshipRequest has status choices
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** its `status` field SHALL accept the values `pending`, `approved`, and `rejected`
- **AND** the default value SHALL be `pending`

#### Scenario: ScholarshipRequest model has __str__
- **WHEN** the `ScholarshipRequest` model is inspected
- **THEN** it SHALL implement `__str__()` returning a human-readable description that includes the submitted `scholarship_name` and the current `status`
