## Context

The admin review flow lives in `scholarships/views.py::admin_request_detail`. On an `approve` POST it unconditionally runs `Scholarship.objects.create(section="IV", foundation_name=request_obj.provider, scholarship_name=request_obj.scholarship_name, ...)`. The `Scholarship` model enforces `unique_together = ["foundation_name", "scholarship_name"]` (`scholarships/models.py`), so any approval whose `(provider, scholarship_name)` already exists — a duplicate request, a re-submission, or a request for an already-listed scholarship — raises `IntegrityError` that Django renders as HTTP 500. A secondary issue: `ScholarshipRequest.objects.get(pk=pk)` raises `DoesNotExist` (also a 500) for an unknown id. The mutation is also not wrapped in a transaction, so a failed insert could in principle leave partial state.

## Goals / Non-Goals

**Goals:**
- Eliminate the 500 on approve: duplicate scholarships are handled gracefully.
- Return 404 (not 500) when a review action targets a non-existent request.
- Make the approve/reject mutation atomic so the request cannot be left half-updated.
- Add regression tests that reproduce the original 500 and lock in the fix.

**Non-Goals:**
- No model/schema changes, no new migrations, no changes to the `unique_together` constraint.
- No deduplication or cleanup of existing catalog rows.
- No UI redesign of the review page; no changes to reject behavior beyond atomicity/404.
- No changes to the public submission flow or non-admin views.

## Decisions

### Decision 1: Use `get_or_create` for the scholarship on approve (preferred over catching `IntegrityError`)
On approve, replace `Scholarship.objects.create(...)` with `Scholarship.objects.get_or_create(foundation_name=..., scholarship_name=..., defaults={...})`. When the row already exists it is returned and linked instead of raising.

- **Why over `try/except IntegrityError`**: `get_or_create` is explicit and atomic within the surrounding transaction; it expresses intent ("there must be exactly one row matching this pair") and naturally degrades to a link rather than requiring retry/rollback logic. Catching `IntegrityError` after a failed insert also leaves the connection in a broken state outside a transaction, which is exactly the bug we are fixing.
- **Why over a pre-check `filter().exists()` then `create()`**: that introduces a TOCTOU race between two concurrent admins; `get_or_create` handles that atomically.

### Decision 2: Link the existing scholarship and mark the request approved, with a distinct message
When `get_or_create` returns an already-existing scholarship (the duplicate case), set `created_scholarship` to it, set `status = "approved"`, and show an info-level message indicating an existing scholarship was linked (rather than the "approved/created" success message). This keeps approval non-destructive and reversible while informing the admin.

### Decision 3: Wrap the mutation in `transaction.atomic()`
The approve branch (and the existing reject branch) SHALL run inside `with transaction.atomic():`. This guarantees the `ScholarshipRequest` status/notes/reviewed_* fields and the `Scholarship` create/link commit together. Combined with `get_or_create`, any concurrent collision is resolved safely.

### Decision 4: Use `get_object_or_404` for the request lookup
Replace `ScholarshipRequest.objects.get(pk=pk)` with `get_object_or_404(ScholarshipRequest, pk=pk)` so an unknown id yields a proper 404 for both GET (review page) and POST (action) instead of a 500.

### Decision 5: Idempotency is preserved
Keep the existing `if request_obj.status != "approved"` guard so re-approving an already-approved request does not create or re-link anything. The idempotency test (`test_approve_is_idempotent`) must continue to pass.

### Decision 6: Fix invalid ternary syntax in the detail template (discovered during verification)
The detail template `admin_request_detail.html` rendered the reviewer name/date with Python-ternary expressions inside `{{ }}` (`{{ request_obj.reviewed_by.name if request_obj.reviewed_by else 'N/A' }}`). Django's template language does not support Python's conditional-expression syntax, so the template fails to compile at parse time — meaning **every** GET to the review URL returned 500 regardless of the request's status. This was the primary user-visible 500.

- **Fix**: Replace both expressions with explicit `{% if request_obj.reviewed_by %}…{% else %}N/A{% endif %}` (and the same pattern for `reviewed_date`). This is idiomatic Django and unambiguous.
- **Why over a `default` filter**: `{% if %}` blocks are clearer for "show this value or a literal fallback", and they avoid subtleties around empty-string resolution when the FK is `None`.
- **Test coverage**: Add GET-render tests for both a pending and a reviewed request so the template compilation path is exercised in CI; both reproduce the original 500 against the unmodified template and pass after the fix.

## Risks / Trade-offs

- **Approving a duplicate silently links an existing scholarship** → An admin might "approve" a request intending to add a new entry but instead links a pre-existing one. Mitigation: the distinct info message and the `created_scholarship` link shown on the review page make this visible; the admin can still reject if unintended.
- **`get_or_create` reusing an unrelated scholarship with the same name/provider** → The unique pair is exactly `(foundation_name, scholarship_name)`, so "same" is well-defined by the model's own contract; this is consistent with how the catalog already dedupes.
- **Concurrent approve by two admins** → `transaction.atomic()` + `get_or_create` serializes safely on the unique constraint; worst case the second approval links the same scholarship and sets reviewed_by to the later admin, which is acceptable.
- **Behavior change vs. current spec wording ("a new Scholarship SHALL be created")** → The spec delta updates this requirement to allow reusing an existing equal scholarship, so spec and code stay aligned.
