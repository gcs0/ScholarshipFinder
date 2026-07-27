## 1. Model & Migration

- [x] 1.1 In `scholarships/models.py`, update `ScholarshipRequest`: remove the `scholarship` ForeignKey; add `scholarship_name` (CharField, max 500, required), `provider` (CharField, max 500, required), `award_amount` (CharField, max 200, blank/default ""), `notes` (TextField, blank/default ""); keep `status`, `admin_notes`, `reviewed_by`, `reviewed_date`, `created_at`, `updated_at`; add nullable `created_scholarship` (ForeignKey to `Scholarship`, null=True, blank=True, on_delete=SET_NULL, related_name="created_from_request").
- [x] 1.2 Update `ScholarshipRequest.__str__()` to return a description including `scholarship_name` and `status` (e.g., `f"Request to add '{self.scholarship_name}' by {self.user.name} ({self.status})"`).
- [x] 1.3 Generate migration `0005_scholarshiprequest_submission_fields.py` (or via `makemigrations`) that: removes the `scholarship` FK, deletes existing `ScholarshipRequest` rows (RunPython no-op forward / no backward restoration), and adds the new fields.
- [x] 1.4 Run `python manage.py migrate scholarships` locally and confirm the schema applies cleanly.

## 2. Form

- [x] 2.1 In `scholarships/forms.py`, update `ScholarshipRequestForm.Meta.fields` to `["scholarship_name", "provider", "award_amount", "notes"]`; mark `scholarship_name` and `provider` required (model-level) and the others optional.
- [x] 2.2 Add widget attrs (placeholder/textarea for `notes`) so the form renders cleanly; remove any reference to a scholarship selector widget.

## 3. URLs

- [x] 3.1 In `scholarships/urls.py`, replace the `/scholarships/<int:scholarship_id>/request/` route with `path("request/", views.request_form, name="request-form")`. Keep the `request-form` name.

## 4. Views

- [x] 4.1 Update `request_form(request)` in `scholarships/views.py`: remove the `scholarship_id` parameter and the lookup of an existing `Scholarship`; on valid POST, create a `ScholarshipRequest` with submitted fields, `user=request.user`, `status="pending"`; redirect to a success page (or `profile`) and show a success message.
- [x] 4.2 Update `profile(request)` so the template receives the user's `ScholarshipRequest` rows (already does — verify it still works without the FK).
- [x] 4.3 Update `admin_request_detail`: on `approve`, if `request_obj.status != "approved"`, create a `Scholarship` from `scholarship_name`/`provider`/`award_amount` (map to `scholarship_name`, `foundation_name`, `contents`; default `section="IV"`), set `created_scholarship`, set `status="approved"`, `reviewed_by`, `reviewed_date`, persist `admin_notes`. On `reject`, set `status="rejected"` and review fields; do not create a `Scholarship`. Guard against duplicate approvals (idempotent).
- [x] 4.4 Verify `admin_requests` still filters/sorts correctly without the FK (no change needed beyond confirming).

## 5. Templates

- [x] 5.1 Update `scholarships/templates/scholarships/request_form.html`: change heading/copy to "Suggest a new scholarship"; render `scholarship_name`, `provider`, `award_amount`, `notes` fields; remove any display of an existing scholarship.
- [x] 5.2 Update `request_success.html` (and/or the redirect target) to confirm "Your suggestion to add a scholarship has been submitted."
- [x] 5.3 Update `profile.html`: list each request showing `scholarship_name`, `provider`, `status` (no link to a specific scholarship).
- [x] 5.4 Update `admin_requests.html` and `admin_request_detail.html`: show `scholarship_name`, `provider`, `award_amount`, `notes`, status, reviewer, and (if present) the `created_scholarship` link.
- [x] 5.5 Remove the "Request this scholarship" button from `scholarship_detail.html` and any per-listing request links.
- [x] 5.6 Add a single "Suggest a scholarship" link to `/request/` in the navigation (`base.html`) visible to authenticated users.

## 6. Admin (Django admin)

- [x] 6.1 Update `scholarships/admin.py` registration for `ScholarshipRequest` to show the new fields (`scholarship_name`, `provider`, `award_amount`, `notes`, `status`, `created_scholarship`, `reviewed_by`) and remove references to the deleted `scholarship` FK.

## 7. Tests

- [x] 7.1 Update `scholarships/tests.py::ModelTests::test_scholarship_request_str` to construct a `ScholarshipRequest` with the new fields (no `Scholarship` FK) and assert `scholarship_name` and `pending` appear in `str(req)`.
- [x] 7.2 Add a test that an authenticated GET to `/request/` renders the form (200) and that an unauthenticated GET redirects to login.
- [x] 7.3 Add a test that a valid POST to `/request/` creates a `ScholarshipRequest` with `status="pending"` owned by the user.
- [x] 7.4 Add a test that approving a request creates a `Scholarship` with the submitted name/provider and links it via `created_scholarship`, and that approving twice does not create a second `Scholarship`.
- [x] 7.5 Add a test that rejecting a request does not create a `Scholarship` and sets `status="rejected"`.

## 8. Validation

- [x] 8.1 Run `ruff check .` and `black .`.
- [x] 8.2 Run `pytest` (or `python manage.py test`) and ensure all tests pass.
- [x] 8.3 Run `python manage.py makemigrations --check --dry-run` to confirm no missing migration.
- [x] 8.4 Run `openspec validate request-new-scholarship-submission --strict` to confirm spec deltas are well-formed.
