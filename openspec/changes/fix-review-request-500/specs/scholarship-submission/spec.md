## MODIFIED Requirements

### Requirement: Admin review detail with approve/reject
The app SHALL provide an admin-only detail page where a reviewer can approve or reject a `ScholarshipRequest`. The approve action SHALL be safe to perform even when a `Scholarship` with the same `foundation_name` and `scholarship_name` already exists, and SHALL NOT raise an unhandled error in that case. Looking up or acting on a `ScholarshipRequest` id that does not exist SHALL return a 404 response, not a 500.

#### Scenario: Approve creates a Scholarship and records it
- **WHEN** an admin submits an `approve` action on a request whose status is not already `approved`
- **AND** no `Scholarship` exists with the same `foundation_name`/`scholarship_name` pair
- **THEN** the request `status` SHALL become `approved`
- **AND** `reviewed_by` SHALL be set to the admin user and `reviewed_date` SHALL be set to the current time
- **AND** a new `Scholarship` row SHALL be created from the submitted `scholarship_name`, `provider`, and `award_amount`
- **AND** the new `Scholarship` SHALL be linked from the request via `created_scholarship`

#### Scenario: Approve reuses an existing equal Scholarship instead of erroring
- **WHEN** an admin submits an `approve` action on a request whose `provider`/`scholarship_name` already matches an existing `Scholarship` row
- **THEN** the system SHALL NOT raise a 500 / `IntegrityError`
- **AND** the request `status` SHALL become `approved`
- **AND** `reviewed_by` and `reviewed_date` SHALL be set
- **AND** no duplicate `Scholarship` SHALL be inserted
- **AND** the request's `created_scholarship` SHALL be linked to the existing matching `Scholarship`
- **AND** the admin SHALL be informed that an existing scholarship was linked

#### Scenario: Approve is idempotent
- **WHEN** an admin submits an `approve` action on a request that is already `approved`
- **THEN** no additional `Scholarship` SHALL be created or re-linked
- **AND** the existing `created_scholarship` link SHALL remain unchanged

#### Scenario: Reject does not create a Scholarship
- **WHEN** an admin submits a `reject` action on a request
- **THEN** the request `status` SHALL become `rejected`
- **AND** `reviewed_by` and `reviewed_date` SHALL be set
- **AND** no `Scholarship` SHALL be created

#### Scenario: Admin notes are persisted
- **WHEN** an admin submits an approve or reject action with an `admin_notes` value
- **THEN** the request's `admin_notes` SHALL be updated with that value

#### Scenario: Detail page renders for a pending request
- **WHEN** an admin issues a GET to the review URL for a `pending` request
- **THEN** the system SHALL return a 200 response rendering the review page
- **AND** the response SHALL NOT raise a template syntax error

#### Scenario: Detail page renders for a reviewed request
- **WHEN** an admin issues a GET to the review URL for a request that has been approved or rejected
- **THEN** the system SHALL return a 200 response rendering the review result
- **AND** the reviewer name and reviewed date SHALL be displayed (or `N/A` when absent)
- **AND** the response SHALL NOT raise a template syntax error

#### Scenario: Unknown request id returns 404
- **WHEN** an admin issues a GET or a POST approve/reject to the review URL for a `ScholarshipRequest` id that does not exist
- **THEN** the system SHALL return a 404 response
- **AND** it SHALL NOT return a 500

#### Scenario: Approve and reject are applied atomically
- **WHEN** an admin submits an `approve` or `reject` action
- **THEN** the status, notes, reviewed_by, reviewed_date, and created_scholarship updates SHALL be applied within a single transaction
- **AND** a failure partway through SHALL NOT leave the `ScholarshipRequest` in a partially updated state
