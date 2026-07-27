## Why

Admins get an HTTP 500 (Server Error) when approving a `ScholarshipRequest` whose `provider`/`scholarship_name` already exists in the catalog. The `Scholarship` model enforces `unique_together = ["foundation_name", "scholarship_name"]`, and the approve path calls `Scholarship.objects.create(...)` without guarding against collisions, so the resulting `IntegrityError` propagates as an unhandled 500. This breaks the review workflow for duplicate or re-submitted scholarships and erodes admin trust in the approval flow.

## What Changes

- Prevent the 500 when approving a request whose scholarship already exists: detect the collision and link the request to the existing `Scholarship` instead of inserting a duplicate (or surface a friendly error message instead of crashing).
- Wrap the approve/reject mutation in a transaction so a failed scholarship creation cannot leave the request in a half-updated state.
- Return a proper 404 (instead of a 500) when an admin opens or acts on a `ScholarshipRequest` id that does not exist.
- Fix the template syntax error in the admin review detail page (`admin_request_detail.html`) that used invalid Python-ternary expressions (`{{ x if c else 'N/A' }}`), which made every GET to the review page return 500.
- Add regression tests covering the duplicate-scholarship approval, idempotent re-approval, missing-request 404, and detail-page rendering for both pending and reviewed requests.

## Capabilities

### New Capabilities
<!-- None. The fix hardens existing behavior rather than introducing a new capability. -->

### Modified Capabilities
- `scholarship-submission`: The "Admin review detail with approve/reject" requirement gains robustness requirements — approving a request whose scholarship already exists SHALL NOT raise a 500, and acting on a missing request SHALL return 404 instead of 500.

## Impact

- **Code**: `scholarships/views.py` (`admin_request_detail`) is the primary change; error handling and transaction boundaries are added.
- **Templates**: `scholarships/templates/scholarships/admin_request_detail.html` has invalid Python-ternary syntax replaced with `{% if %}` blocks.
- **Models**: No schema changes to `scholarship-models`; the `Scholarship` unique constraint and `ScholarshipRequest` fields are unchanged.
- **Tests**: `scholarships/tests.py` (`AdminReviewTests`) gains duplicate-approval, missing-request, idempotency-identity, and detail-page render cases.
- **APIs/Dependencies**: No URL or external API changes.
- **User-facing**: Admins can view and act on review requests without hitting a 500; approving a duplicate shows a clear info message rather than a crash page.
