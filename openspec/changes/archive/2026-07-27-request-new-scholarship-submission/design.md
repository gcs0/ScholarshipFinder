## Context

The `ScholarshipRequest` model and surrounding views/forms/templates were built as a "request to receive a listed scholarship" flow: a `ScholarshipRequest` row holds a foreign key to an existing `Scholarship`, the form is reachable only at `/scholarships/<id>/request/`, and admin review simply flips a `status` field. The product intent (and the original `scholarship-models` spec) is different: a user should *suggest a new scholarship* that is **not yet listed** and an admin should review the suggestion and, on approval, optionally create a `Scholarship` row from it.

The implementation drifted from the spec, so this change realigns model, form, views, URLs, templates, admin, tests, and the database schema with the intended "submit a new scholarship" semantics.

Relevant files:
- `scholarships/models.py` — `ScholarshipRequest` (currently has `scholarship` FK).
- `scholarships/forms.py` — `ScholarshipRequestForm` (currently a scholarship selector).
- `scholarships/views.py` — `request_form`, `profile`, `admin_requests`, `admin_request_detail`.
- `scholarships/urls.py` — `request-form` route tied to a scholarship id.
- `scholarships/templates/scholarships/{request_form,request_success,admin_requests,admin_request_detail,profile,scholarship_detail}.html`.
- `scholarships/migrations/` — last migration is `0004_alter_scholarship_plural_grants_and_more.py`.
- `scholarships/tests.py` — `test_scholarship_request_str` asserts the old FK-based behavior.

## Goals / Non-Goals

**Goals:**
- Realign `ScholarshipRequest` with the spec: capture user-submitted details about a scholarship not yet in the system.
- Provide a standalone submission form (no existing-scholarship dependency).
- Let an admin review submissions; approving creates a `Scholarship` row from the submitted data.
- Keep the auth/admin permission model (`@login_required` for submit, `is_superuser` for review) unchanged.
- Make the model change via a migration that drops the old FK and adds the new fields.

**Non-Goals:**
- No change to the `User` or `Scholarship` core field sets (beyond populating a new `Scholarship` from a request on approval).
- No authentication, registration, or password-reset changes.
- No preservation of pre-existing `ScholarshipRequest` rows (their semantics are invalid under the new model).
- No email notifications, file attachments, or rich-text submissions in this change.
- No public/anonymous submissions — submissions remain an authenticated-user action.

## Decisions

### Decision 1: Denormalize scholarship details onto `ScholarshipRequest` (no FK to `Scholarship`)
Keep `ScholarshipRequest` self-describing: store `scholarship_name`, `provider`, `award_amount`, and `notes` directly. The request must outlive any `Scholarship` row (a request is for a scholarship that does not yet exist), so a FK is wrong.

- **Alternative considered**: Keep a nullable FK and only fill it when a `Scholarship` is created on approval. Rejected because it perpetuates the confusing dual meaning (request-for-existing vs. request-for-new) and complicates the form/URL contract.
- **Alternative considered**: A generic `Proposal` table with JSON detail blob. Rejected — typed columns are simpler and match the existing spec.

### Decision 2: Capture review metadata on the request itself
Keep the existing `status` (`pending`/`approved`/`rejected`), `admin_notes`, `reviewed_by`, `reviewed_date` fields. They are already correct for the workflow and require no schema change beyond retaining them.

### Decision 3: Standalone submission URL `/request/`
Replace `/scholarships/<int:scholarship_id>/request/` with `/request/`. The view no longer takes a `scholarship_id` parameter. The `name="request-form"` URL name is kept so internal references resolve (existing `redirect("profile")` calls still work).

- **Alternative considered**: Keep the old URL and ignore the id. Rejected — misleading and would still surface on per-scholarship pages.

### Decision 4: On admin approval, create a `Scholarship` row from the submission
When an admin approves, the view constructs a `Scholarship` from `scholarship_name` + `provider` + `award_amount` (mapped into `Scholarship` fields: `scholarship_name`, `foundation_name`, `contents` for the award text) and stores a back-reference via a new nullable `created_scholarship` FK on `ScholarshipRequest` so reviewers can see what was produced. Section defaults to `"IV"` (Private Foundations) since submissions are typically private; admin can edit afterward.

- **Alternative considered**: Do not auto-create; admin copies details manually. Rejected as poor UX and error-prone.
- **Alternative considered**: Always require the submitter to pick a section. Rejected — adds friction; defaulting + post-edit is simpler.

### Decision 5: Migration drops old FK column and invalid rows
The migration removes the `scholarship` FK, removes existing rows (their semantics are invalid), and adds `scholarship_name`, `provider`, `award_amount`, `notes`, and `created_scholarship` (nullable FK to `Scholarship`, `null=True, on_delete=SET_NULL`). Using a single `AlterModelTable`/`RemoveField`/`AddField` migration keeps rollback straightforward.

### Decision 6: `ScholarshipRequestForm` fields
Form exposes `scholarship_name` (required), `provider` (required), `award_amount` (optional CharField to match `Scholarship.contents` free-text conventions), and `notes` (optional Textarea). It does not expose `status`/`user`/review fields — those are set by the view/server.

## Risks / Trade-offs

- **[Risk] Loss of existing request rows** → Mitigation: migration explicitly deletes them; documented as BREAKING in the proposal. Acceptable because the old semantics were invalid.
- **[Risk] Duplicate scholarships created by repeated approvals** → Mitigation: the approve action is a single POST that sets `status="approved"`; the view guards with `if request_obj.status != "approved"` before creating the `Scholarship`, and sets `created_scholarship` immediately so re-submits are no-ops.
- **[Risk] Ambiguous section when creating `Scholarship`** → Mitigation: default to `"IV"` and surface it in the admin review screen for editing in a follow-up; out of scope to add a section picker here (Non-Goal).
- **[Risk] Broken inbound links to `/scholarships/<id>/request/`** → Mitigation: this is an internal-only app; the per-scholarship "Request" button is removed in the same change. Acceptable BREAKING.
- **[Trade-off] Free-text `award_amount`** rather than integer — chosen to match `Scholarship.contents` conventions (ranges, units); sacrifices easy numeric filtering on submitted amounts.

## Migration Plan

1. Merge code + migration; deploy.
2. Run `python manage.py migrate scholarships` — drops FK + adds new fields, clears invalid rows.
3. Smoke test: log in as a user, submit a new-scholarship request, log in as admin, approve it, confirm a `Scholarship` row was created.
4. Rollback (if needed): `python manage.py migrate scholarships 0004` reverts the schema; revert the code deploy. Pre-existing rows are not restored (acceptable per proposal).

## Open Questions

- Should the admin review screen allow inline editing of section/provider before creating the `Scholarship`? (Default: no — create with defaults, edit via Django admin afterwards. Revisit if reviewers ask for it.)
- Should submissions be rate-limited per user? (Default: no — authenticated users only; revisit if spam appears.)
