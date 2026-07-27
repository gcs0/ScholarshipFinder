## 1. Regression tests (write first to reproduce the 500)

- [x] 1.1 Add `test_approve_links_existing_scholarship_on_duplicate` to `AdminReviewTests`: pre-create a `Scholarship` with the request's `provider`/`scholarship_name`, POST `approve`, assert status becomes `approved`, no duplicate `Scholarship` is inserted, `created_scholarship` points at the pre-existing row, and the response is a 302 (no 500).
- [x] 1.2 Add `test_review_unknown_request_returns_404` covering GET and POST to `admin-request-detail` with a non-existent pk; assert 404 for both.
- [x] 1.3 Add `test_approve_reject_atomic` (or assertion) verifying the existing idempotency and reject tests still pass after the refactor.
- [x] 1.4 Run the new tests against the unmodified view to confirm they reproduce the 500/404 failures (red baseline).

## 2. Fix `admin_request_detail` in `scholarships/views.py`

- [x] 2.1 Import `get_object_or_404` from `django.shortcuts` and `transaction` from `django.db`.
- [x] 2.2 Replace `ScholarshipRequest.objects.get(pk=pk)` with `get_object_or_404(ScholarshipRequest, pk=pk)` so unknown ids return 404 on both GET and POST.
- [x] 2.3 Wrap the POST approve/reject mutation in `with transaction.atomic():`.
- [x] 2.4 Replace the `Scholarship.objects.create(...)` call inside the approve branch with `Scholarship.objects.get_or_create(foundation_name=request_obj.provider, scholarship_name=request_obj.scholarship_name, defaults={...})`, capturing the `created` boolean.
- [x] 2.5 Set `request_obj.created_scholarship` to the returned scholarship (newly created or existing) and set `status = "approved"`; preserve the `status != "approved"` idempotency guard so re-approval does not re-link or re-create.
- [x] 2.6 Show an info `messages` notice when `get_or_create` linked an existing scholarship (`created is False`), and keep the existing success message otherwise.

## 3. Verify and finalize

- [x] 3.1 Run `pytest` and confirm all existing tests plus the new regression tests pass (green).
- [x] 3.2 Run `ruff check .` and `black --check .`; fix any issues introduced.
- [x] 3.3 Manually sanity-check: approve a request for an already-existing scholarship in a local run, confirm no 500 and the existing scholarship is linked.

## 4. Template syntax fix (`admin_request_detail.html`) — discovered during verification

- [x] 4.1 Add regression tests `test_detail_page_renders_for_pending_request` and `test_detail_page_renders_for_reviewed_request` that GET the detail page and assert 200; confirm both fail with the production `TemplateSyntaxError` against the unmodified template (red baseline).
- [x] 4.2 Replace the invalid Python-ternary expressions in `admin_request_detail.html` (`{{ ... if ... else 'N/A' }}`) for `reviewed_by` and `reviewed_date` with idiomatic `{% if %}`/`{% else %}`/`{% endif %}` blocks.
- [x] 4.3 Re-run the full suite; confirm the two render tests and all prior tests pass (green).
