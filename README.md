# Basic Twitter Clone API

This repository contains a small Flask-based backend that mimics a portion of Twitter's feature set: users can register, authenticate via JWT, post tweets, retrieve historical tweets, and delete them. The service now ships with Docker support, an environment-driven configuration, and a faster database layer.

## Quickstart

### Run with Docker (recommended)

```bash
docker compose up --build
```

The compose stack provisions both the API (`http://localhost:8000`) and a Postgres database. Default credentials are defined in `docker-compose.yml`; override them in a `.env` file or via environment variables before starting the stack for production use.

### Run locally with Python

```bash
cd tweetdbapi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Example configuration for SQLite (default) or Postgres
export DATABASE_URL=sqlite:///app/tweets.db
export JWT_SECRET_KEY=change-this-jwt-secret
export SECRET_KEY=change-this-flask-secret

python run.py  # or: FLASK_DEBUG=1 python run.py for hot reload
```

`DATABASE_URL` accepts any SQLAlchemy-compatible connection string (e.g. `postgresql+psycopg2://user:pass@host:5432/db`). When not provided, the service falls back to an embedded SQLite database stored in `app/tweets.db`.

## Configuration Reference

| Variable         | Description                                                 | Default (development)        |
| ---------------- | ----------------------------------------------------------- | ---------------------------- |
| `DATABASE_URL`   | SQLAlchemy database connection string                       | `sqlite:///app/tweets.db`    |
| `JWT_SECRET_KEY` | Secret used to sign access tokens                           | `change-this-jwt-secret`     |
| `SECRET_KEY`     | Flask session/CSRF signing key                              | `change-this-flask-secret`   |
| `PORT`           | Bind port when running via `run.py` or Gunicorn             | `5000` (run.py) / `8000` (Docker) |
| `FLASK_DEBUG`    | Enables Flask debug server when set to `1` (local dev only) | `0`                          |

## What Changed

- Environment-driven setup with sensible defaults (SQLite locally, Postgres via `DATABASE_URL`).
- Faster ORM operations using bulk deletes and reduced round-trips.
- Consistent JSON error messages and HTTP status codes for easier client handling.
- Dockerfile + `docker-compose.yml` for single-command bootstrap, plus Gunicorn-based production entrypoint.
- Procfile updated to target the new `run:app` module layout.

## API Overview

All endpoints live under the base URL (e.g. `http://localhost:8000`). Responses are JSON and include informative error payloads with appropriate HTTP status codes.

### 1. Add User - `POST /add_user`

Request body:

```json
{
  "username": "alice"
}
```

Success response (`201 Created`):

```json
{
  "user_id": "al5fea1c0",
  "username": "alice",
  "normalized_username": "alice",
  "access_token": "<jwt>",
  "created_timestamp": "2025-11-02T12:34:56.789123"
}
```

Duplicate usernames return `409 Conflict` with an `error` message.

### 2. Create Tweet - `POST /add_tweet`

Requires a valid JWT in the `Authorization: Bearer <token>` header.

Request body:

```json
{
  "uname": "alice",
  "tweetbody": "Hello Flask!"
}
```

Response (`201 Created`):

```json
{
  "tweet_id": "9f0cbb5ef1b243879676742e3a0f6d87",
  "created_timestamp": "2025-11-02T12:35:10.123456"
}
```

Tweet length is enforced (2?140 characters). Invalid payloads return `400 Bad Request`; authentication mismatches return `401 Unauthorized`.

### 3. Tweet History - `POST /tweet_hist`

Body parameters:

```json
{
  "uname": "alice",
  "grtndate": "01/11/2025"
}
```

Returns tweets created on or after the supplied date (inclusive) ordered by timestamp.

```json
{
  "num_of_tweets": 2,
  "tweets": [
    {
      "tweet_id": "...",
      "tweet_text": "Hello Flask!",
      "created_timestamp": "2025-11-02T12:35:10.123456"
    },
    {
      "tweet_id": "...",
      "tweet_text": "Second post",
      "created_timestamp": "2025-11-02T13:01:02.456789"
    }
  ]
}
```

An empty result is returned as `404 Not Found` with `{"error": "tweets not found"}`.

### 4. Delete Tweets - `DELETE /tweet_delete?username=<name>`

Deletes all tweets for the authenticated user and returns a summary of what was removed.

```json
{
  "num_of_tweets": 2,
  "tweets": [
    { "tweet_id": "...", "tweet_text": "Hello Flask!" },
    { "tweet_id": "...", "tweet_text": "Second post" }
  ]
}
```

### 5. Refresh Token - `POST /refresh_token`

Request body:

```json
{
  "username": "alice"
}
```

Response (`200 OK`):

```json
{
  "username": "alice",
  "normalized_username": "alice",
  "access_token": "<new jwt>"
}
```

## Legacy UI Screenshots

Images in this repository (`adduser_good.png`, `web1.png`, etc.) show the original front-end connected to the API. The JSON response shape has since been improved (nested structures instead of comma-separated strings), so the UI may require adjustments to match the current API output.

## Future Enhancements

- Add automated database migrations (Alembic) for schema evolution.
- Extend test coverage for API routes and database helpers.
- Introduce rate limiting and request validation middleware.
- Explore Redis-based caching for frequently accessed timelines.
