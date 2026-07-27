# scholarship-favorites Specification

## ADDED Requirements

### Requirement: Favorite model
The `scholarships` app SHALL define a `Favorite` model that records a single user's interest in a single scholarship.

#### Scenario: Favorite model has expected fields
- **WHEN** the `Favorite` model is inspected
- **THEN** it SHALL have a `user` field that is a ForeignKey to `User` with `on_delete=CASCADE`
- **AND** it SHALL have a `scholarship` field that is a ForeignKey to `Scholarship` with `on_delete=CASCADE`
- **AND** it SHALL have a `created_at` field set automatically on creation

#### Scenario: Favorite is unique per user and scholarship
- **WHEN** the `Favorite` model is inspected
- **THEN** it SHALL enforce uniqueness such that a given `User` can have at most one `Favorite` for a given `Scholarship`
- **AND** the uniqueness SHALL be declared via a `UniqueConstraint` (or `unique_together`) on (`user`, `scholarship`)

#### Scenario: Favorite ordering
- **WHEN** favorites are queried without an explicit order
- **THEN** they SHALL be ordered by most recently created first (descending `created_at`)

#### Scenario: Favorite model has __str__
- **WHEN** the `Favorite` model is inspected
- **THEN** it SHALL implement `__str__()` returning a human-readable description that includes the user and the scholarship

### Requirement: Favorite toggle requires authentication
The favorite and unfavorite actions SHALL be available only to authenticated users.

#### Scenario: Unauthenticated favorite attempt is rejected
- **WHEN** an unauthenticated user issues a request to the favorite action URL for a scholarship
- **THEN** the system SHALL redirect to the login page (or return `403`)
- **AND** no `Favorite` row SHALL be created

### Requirement: Favorite action creates a Favorite
The app SHALL provide an endpoint that adds a scholarship to the requesting user's favorites.

#### Scenario: Successful favorite
- **WHEN** an authenticated user issues a POST to the favorite endpoint for a scholarship they have not yet favorited
- **THEN** a `Favorite` row SHALL be created with `user` set to the authenticated user and `scholarship` set to the target scholarship

#### Scenario: Idempotent favorite
- **WHEN** an authenticated user issues a POST to the favorite endpoint for a scholarship they have already favorited
- **THEN** no duplicate `Favorite` SHALL be created
- **AND** the response SHALL still indicate the favorited state

### Requirement: Unfavorite action removes a Favorite
The app SHALL provide an endpoint that removes a scholarship from the requesting user's favorites.

#### Scenario: Successful unfavorite
- **WHEN** an authenticated user issues a POST to the unfavorite endpoint for a scholarship they have favorited
- **THEN** the matching `Favorite` row SHALL be deleted

#### Scenario: Unfavorite is idempotent
- **WHEN** an authenticated user issues a POST to the unfavorite endpoint for a scholarship they have not favorited
- **THEN** the request SHALL succeed without error
- **AND** no `Favorite` row SHALL exist for that user and scholarship

### Requirement: Favorite toggle returns an HTMX-friendly response
The favorite and unfavorite endpoints SHALL return a small HTML fragment suitable for in-place swapping, and SHALL render the correct toggled state.

#### Scenario: HTMX favorite response renders the unfavorite button
- **WHEN** an authenticated user favorites a scholarship via an HTMX request
- **THEN** the response SHALL be an HTML fragment representing the unfavorite (active) state for that scholarship

#### Scenario: HTMX unfavorite response renders the favorite button
- **WHEN** an authenticated user unfavorites a scholarship via an HTMX request
- **THEN** the response SHALL be an HTML fragment representing the favorite (inactive) state for that scholarship

#### Scenario: Non-HTMX fallback redirects
- **WHEN** an authenticated user favorites or unfavorites a scholarship via a normal (non-HTMX) request
- **THEN** the system SHALL redirect to a sensible location (the scholarship detail or the referring page)

### Requirement: My Favorites page
The app SHALL provide an authenticated page that lists the scholarships the current user has favorited.

#### Scenario: Favorites page is auth-only
- **WHEN** an unauthenticated user issues a request to the favorites URL
- **THEN** the system SHALL redirect to the login page

#### Scenario: Favorites page lists the user's favorited scholarships
- **WHEN** an authenticated user views their favorites page
- **THEN** the page SHALL list each scholarship the user has favorited, ordered by most recently favorited first
- **AND** each entry SHALL expose an unfavorite control

#### Scenario: Empty favorites state
- **WHEN** an authenticated user with no favorites views their favorites page
- **THEN** the page SHALL display an empty-state message

### Requirement: Favorite indicator appears on scholarship listings and detail
The scholarship card (in list/search results) and the scholarship detail page SHALL display a favorite control reflecting whether the current user has favorited that scholarship.

#### Scenario: Favorited state is reflected for authenticated users
- **WHEN** an authenticated user views a scholarship they have favorited
- **THEN** the rendered control SHALL show the active/favorited state

#### Scenario: Favorite control is hidden for anonymous users
- **WHEN** an anonymous user views a scholarship
- **THEN** the page SHALL NOT offer a functional favorite toggle (or SHALL prompt login)
