# scholarship-submission Spec

## ADDED Requirements

### Requirement: Standalone scholarship submission URL
The app SHALL expose a standalone URL for submitting a new-scholarship request that does not depend on an existing `Scholarship` row.

#### Scenario: Submit URL is independent of a scholarship id
- **WHEN** the URL configuration is inspected
- **THEN** there SHALL be a route mapped to `/request/` (URL name `request-form`)
- **AND** the route SHALL NOT require a scholarship id parameter

#### Scenario: Submit URL requires authentication
- **WHEN** an unauthenticated user issues a GET to `/request/`
- **THEN** the system SHALL redirect to the login page

### Requirement: Scholarship submission form
The app SHALL provide a form that captures the details of a scholarship the user wants added to the system.

#### Scenario: Form fields
- **WHEN** the submission form is rendered
- **THEN** it SHALL present inputs for `scholarship_name`, `provider`, `award_amount`, and `notes`
- **AND** `scholarship_name` and `provider` SHALL be required

#### Scenario: Form does not offer existing scholarships
- **WHEN** the submission form is rendered
- **THEN** it SHALL NOT include a selector for an existing `Scholarship`

### Requirement: Submission creates a pending request
The app SHALL create a `ScholarshipRequest` row in the `pending` status when a user submits a valid form.

#### Scenario: Successful submission
- **WHEN** an authenticated user submits a valid form to `/request/`
- **THEN** a `ScholarshipRequest` SHALL be created with `user` set to the authenticated user
- **AND** `status` SHALL be `pending`
- **AND** the user SHALL be redirected to a success/profile page

#### Scenario: Invalid submission
- **WHEN** an authenticated user submits an invalid form to `/request/`
- **THEN** the system SHALL re-render the form with validation errors
- **AND** no `ScholarshipRequest` SHALL be created

### Requirement: Users can view their own submissions
The app SHALL list the authenticated user's `ScholarshipRequest` submissions on their profile page.

#### Scenario: Profile lists user requests
- **WHEN** the user views their profile
- **THEN** the page SHALL list that user's `ScholarshipRequest` rows ordered by most recent first
- **AND** each entry SHALL show the submitted `scholarship_name`, `provider`, and current `status`

### Requirement: Admin review list
The app SHALL provide an admin-only page that lists `ScholarshipRequest` rows for review.

#### Scenario: Admin requests page is admin-only
- **WHEN** a non-superuser issues a request to the admin requests URL
- **THEN** the system SHALL deny access

#### Scenario: Admin requests page supports status filter
- **WHEN** an admin opens the requests page with a `status` query parameter of `pending`, `approved`, `rejected`, or `all`
- **THEN** the page SHALL list only the requests matching that status (or all when `all`/omitted)
- **AND** the rows SHALL be ordered by most recent first

### Requirement: Admin review detail with approve/reject
The app SHALL provide an admin-only detail page where a reviewer can approve or reject a `ScholarshipRequest`.

#### Scenario: Approve creates a Scholarship and records it
- **WHEN** an admin submits an `approve` action on a request whose status is not already `approved`
- **THEN** the request `status` SHALL become `approved`
- **AND** `reviewed_by` SHALL be set to the admin user and `reviewed_date` SHALL be set to the current time
- **AND** a new `Scholarship` row SHALL be created from the submitted `scholarship_name`, `provider`, and `award_amount`
- **AND** the new `Scholarship` SHALL be linked from the request via `created_scholarship`

#### Scenario: Approve is idempotent
- **WHEN** an admin submits an `approve` action on a request that is already `approved`
- **THEN** no additional `Scholarship` SHALL be created
- **AND** the existing `created_scholarship` link SHALL remain unchanged

#### Scenario: Reject does not create a Scholarship
- **WHEN** an admin submits a `reject` action on a request
- **THEN** the request `status` SHALL become `rejected`
- **AND** `reviewed_by` and `reviewed_date` SHALL be set
- **AND** no `Scholarship` SHALL be created

#### Scenario: Admin notes are persisted
- **WHEN** an admin submits an approve or reject action with an `admin_notes` value
- **THEN** the request's `admin_notes` SHALL be updated with that value

### Requirement: Per-scholarship request entry point is removed
The app SHALL NOT expose a "request this scholarship" action tied to an existing scholarship.

#### Scenario: Scholarship detail has no receive-request action
- **WHEN** the scholarship detail template is rendered
- **THEN** it SHALL NOT render a link to submit a request to receive that specific scholarship

#### Scenario: Navigation offers a generic submit link
- **WHEN** an authenticated user views the navigation
- **THEN** it SHALL offer a single link to `/request/` labeled to indicate submitting a new scholarship
