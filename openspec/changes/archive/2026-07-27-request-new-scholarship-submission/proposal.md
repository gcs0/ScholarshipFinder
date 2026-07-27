## Why

The current "Request" feature is misused: it lets a user request to *receive* an existing scholarship (the request is tied to a `Scholarship` row via foreign key and the URL `/scholarships/<id>/request/`). The intended purpose is for a user to *suggest a new scholarship* to be added to the system — one that is not yet listed. This change realigns the feature with that intent (and with the existing `scholarship-models` spec, which already describes `ScholarshipRequest` as "user-submitted requests not yet listed" with `scholarship_name`, `provider`, `award_amount`, and `notes`).

## What Changes

- **BREAKING**: Replace the `ScholarshipRequest.scholarship` ForeignKey with denormalized submission fields (`scholarship_name`, `provider`, `award_amount`, `notes`) describing a scholarship the user wants added.
- **BREAKING**: Replace the `/scholarships/<id>/request/` URL with a standalone `/request/` URL so users can submit a new scholarship suggestion without an existing scholarship.
- Update `ScholarshipRequestForm` to capture scholarship details (name, provider, award amount, notes) instead of a scholarship selector.
- Update `request_form` view to no longer require a `scholarship_id` and to create requests with the submitted details.
- Update the user-facing `request_form.html`, `request_success.html`, and `profile.html` templates to reflect "submit a new scholarship" wording.
- Update admin review (`admin_requests.html`, `admin_request_detail.html`) to display the submitted scholarship details and, on approval, optionally create a new `Scholarship` row from the submitted data.
- Add a data migration that drops the old FK column and adds the new submission fields (existing rows are not portable; the migration will remove them since the old semantics are invalid).

## Capabilities

### New Capabilities
- `scholarship-submission`: User-facing and admin-facing workflow for submitting, reviewing, and approving new scholarship suggestions (form submission, success page, profile listing, admin review dashboard, approval that creates a `Scholarship`).

### Modified Capabilities
- `scholarship-models`: `ScholarshipRequest` requirements are clarified/expanded so the model captures denormalized scholarship details (`scholarship_name`, `provider`, `award_amount`, `notes`) plus review workflow fields (`status`, `admin_notes`, `reviewed_by`, `reviewed_date`), and is no longer linked to an existing `Scholarship`.

## Impact

- **Code**: `scholarships/models.py`, `scholarships/forms.py`, `scholarships/views.py`, `scholarships/urls.py`, `scholarships/admin.py`, and the `request_*` / `admin_request*` / `profile.html` templates.
- **Database**: New migration altering the `scholarships_scholarshiprequest` table (drop FK + add fields). Existing rows are discarded.
- **APIs/URLs**: `request-form` URL changes from `/scholarships/<id>/request/` to `/request/`; `scholarship-detail` template's "Request" button is removed (or repurposed to a generic "Suggest a scholarship" link in the nav/profile).
- **Tests**: Existing `ScholarshipRequest`-related tests in `scholarships/tests.py` must be updated to the new semantics.
