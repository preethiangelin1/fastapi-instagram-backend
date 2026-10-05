# InstaClone API

A FastAPI backend for a photo-sharing application. It provides user registration and bearer-token authentication, posts, comments, likes, follows, a cursor-paginated feed, password recovery, and presigned object-storage uploads.

## Features

- Async SQLAlchemy persistence with Alembic migrations.
- Password hashing and JWT access tokens.
- Public and private user accounts. Follow requests to private accounts remain pending until accepted or rejected.
- Posts with captions and image references, plus comments and likes.
- A feed containing the signed-in user's posts and posts from accepted follows and public accounts.
- Presigned S3-compatible image uploads and CDN image URLs.
- SMTP password-reset email delivery.
- Logfire instrumentation for FastAPI, Pydantic, SQLAlchemy, and selected user actions.

## Requirements

- Python 3.14 or newer.
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management.
- A PostgreSQL database (the application uses the `psycopg` async driver). The database must be reachable using both direct and pooled URLs.
- An S3-compatible bucket and CDN domain for the presigned upload and post creation flow.
- An SMTP server if password reset email delivery is needed.

## Configuration

Copy `.env.example` to `.env` and update the values for your environment. Keep `.env` and all credentials out of version control.

## Install and run

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev main.py
```

The development server listens at `http://127.0.0.1:8000`. For a production-style local server, use `uv run fastapi run main.py`. The root page (`/`) serves the included HTML landing page. Interactive API docs are available at `/docs`; the OpenAPI document is at `/openapi.json`.

## Authentication

Register through `POST /api/v1/users/`, then obtain a token through `POST /api/v1/login`. Login uses OAuth2 form fields (`username` and `password`), not a JSON body. Send the returned token on protected routes:

```http
Authorization: Bearer <access_token>
```

Tokens carry the username and expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (30 minutes by default). Passwords must be at least eight characters. The login token URL exposed in the OAuth2 scheme is `/api/v1/login`.

## API overview

All listed routes use the `/api/v1` prefix unless shown as `/`.

| Method | Path | Purpose | Authentication |
| --- | --- | --- | --- |
| `POST` | `/api/v1/users/` | Register. Body: `username`, `email`, `full_name`, `password`, `is_private`. | No |
| `POST` | `/api/v1/login` | Log in with form fields `username` and `password`; returns a bearer token. | No |
| `POST` | `/api/v1/users/forgot-password` | Request a reset email using `{ "email": "..." }`. The response does not reveal whether the account exists. | No |
| `POST` | `/api/v1/users/reset-password` | Reset using `{ "token": "...", "new_password": "..." }`. | No |
| `PATCH` | `/api/v1/users/me/password` | Change password using `current_password` and `new_password`. | Yes |
| `POST` | `/api/v1/uploads/presign` | Request a short-lived image upload URL with `{ "content_type": "image/jpeg" }`. Supported types: JPEG, PNG, WebP. Returns `upload_url`, `key`, and `cdn_url`. | Yes |
| `POST` | `/api/v1/posts/` | Create a post with `{ "caption": "...", "image_file": "<uploaded key>" }`. The API verifies that the object exists in storage. | Yes |
| `GET` | `/api/v1/posts/{id}` | Fetch a post with author, comments, and likes. | Yes |
| `DELETE` | `/api/v1/posts/{id}` | Delete your own post and its stored image. | Yes |
| `GET` | `/api/v1/feed/` | Fetch visible posts. Accepts `limit` (default 20) and the paired cursor fields `cursor_created_at` and `cursor_id`. | Yes |
| `GET` | `/api/v1/posts/{post_id}/comments` | List comments on a post. | Yes |
| `POST` | `/api/v1/posts/{post_id}/comments` | Add a comment using `{ "text": "..." }`. | Yes |
| `PATCH` | `/api/v1/posts/{post_id}/comments/{comment_id}` | Edit your own comment using `{ "text": "..." }`. | Yes |
| `DELETE` | `/api/v1/posts/{post_id}/comments/{comment_id}` | Delete your own comment. | Yes |
| `GET` | `/api/v1/posts/{post_id}/likes` | List likes on a post. | Yes |
| `POST` | `/api/v1/posts/{post_id}/likes` | Like a post. | Yes |
| `POST` | `/api/v1/users/{user_id}/follows` | Follow a user; private accounts create a pending request. | Yes |
| `GET` | `/api/v1/users/me/followers` | List accepted followers of the current user. | Yes |
| `PATCH` | `/api/v1/users/me/follows/{follower_id}` | Accept or reject a follow request using `{ "status": "accepted" }` or `{ "status": "rejected" }`. | Yes |

The feed response contains `posts`, `has_more`, and `next_cursor`. When `has_more` is true, pass the cursor's `created_at` and `id` as `cursor_created_at` and `cursor_id` to fetch the next page. The feed defaults to 20 items; choose a reasonable `limit` for your client.

### Uploading a post image

1. Call `POST /api/v1/uploads/presign` with an allowed `content_type`.
2. Upload the image bytes to the returned `upload_url` using HTTP `PUT` and the same `Content-Type` value used to request the URL. The URL expires after 60 seconds.
3. Call `POST /api/v1/posts/` with the returned `key` as `image_file` and a caption.

Example post body:

```json
{
  "caption": "Golden hour",
  "image_file": "posts/42/your-upload-id.jpg"
}
```

Post responses include `image_path`, formed from `CLOUDFRONT_DOMAIN` and the stored image key.

## Database migrations

Apply migrations before serving requests:

```bash
uv run alembic upgrade head
```

To create a migration after changing SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

## Tests and tools

```bash
uv run pytest
uv run ruff check .
```

The repository includes schema and analytics tests, plus a Locust workload in `locustfile.py`. A demo-data script is also available:

```bash
SEED_PASSWORD='use-a-demo-password' uv run python seed_data.py
```

Start the API first and configure storage, database, and `SEED_PASSWORD`. The script creates demo users, uploads sample images, and populates posts, comments, and likes. It accepts `--api-url` (default `http://127.0.0.1:8000`) or the `API_URL` environment variable.

## Project layout

```text
main.py                 FastAPI app, lifespan, and router registration
config.py               Environment-backed application settings
routers/                HTTP endpoints grouped by feature
auth/                   OAuth2 bearer auth and JWT handling
db/                     SQLAlchemy models, database session, and data operations
integrations/s3.py      S3-compatible storage operations and presigned URLs
schemas.py              Pydantic request and response models
alembic/                Database migration environment and revisions
templates/              Homepage and password-reset email templates
tests/                  Automated tests
```

## Current behavior notes

- The service currently requires its database, object-storage, CDN, and signing-key settings at startup, even when developing a feature that does not use every integration.
- The legacy `POST /api/v1/posts/image-upload` route writes files under `media/posts/`; the normal post creation flow instead uses presigned object-storage uploads.
- The application does not mount the local `media/` directory as static content.
- `POST /api/v1/posts/` requires the image object to exist in storage first.
- Observability calls `logfire.configure()` at application startup; configure Logfire credentials/environment as desired for your deployment.
