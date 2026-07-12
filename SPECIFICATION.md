# Kudos System Specification

## Functional Requirements

### User Stories

1. As a user, I can authenticate (simple session-based login) to the internal app.
2. As a user, I can select another user from a dropdown list to receive kudos.
3. As a user, I can write a message of appreciation (max 500 characters).
4. As a user, I can submit the kudos which gets stored in the database.
5. As a user, I can view a public feed of recent kudos on the main dashboard.
6. As an administrator, I can hide or delete inappropriate kudos messages (content moderation).

### Acceptance Criteria

- Authentication: users must be identified; simple session login is acceptable for prototype.
- User selection: recipient list excludes the current user.
- Message length: max 500 characters; validated server-side.
- Feed: shows most recent kudos where `is_visible = true`.
- Moderation: admins can toggle `is_visible` or delete kudos; moderation actions are recorded with `moderated_by` and `moderated_at`.

## Technical Design

### Database Schema

- `users` table
  - `id` INTEGER PRIMARY KEY
  - `name` TEXT NOT NULL

- `kudos` table
  - `id` INTEGER PRIMARY KEY
  - `sender_id` INTEGER REFERENCES users(id)
  - `recipient_id` INTEGER REFERENCES users(id)
  - `message` TEXT NOT NULL
  - `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
  - `is_visible` BOOLEAN DEFAULT 1
  - `moderated_by` INTEGER REFERENCES users(id) NULLABLE
  - `moderated_at` DATETIME NULLABLE
  - `reason_for_moderation` TEXT NULLABLE

### API Endpoints

- `GET /` — Dashboard feed: returns recent visible kudos.
- `GET /kudos/new` — Form to submit a kudos.
- `POST /kudos/new` — Submit kudos (payload: `recipient_id`, `message`).
- `GET /login?user_id=<id>` — Simple login helper (sets session user).
- `POST /admin/moderate/<kudos_id>` — Toggle visibility or delete (admin-only).

## Implementation Notes

- The prototype implementation in `app.py` uses `is_visible` and moderation fields to track moderation actions.
- Admin is identified by `user.id == 1` in the prototype; replace with real role checks in production.
