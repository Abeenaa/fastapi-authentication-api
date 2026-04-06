# FastAPI Authentication API

Backend task for building an Authentication System using FastAPI and SQLite.

## Overview

This API provides a complete authentication flow for frontend and mobile developers:

- Register users with hashed passwords
- Login with JWT generation (access + refresh token)
- Get logged-in user details
- Delete accounts
- Example Email Verification simulation (Generating 6-digit code and validating it)

Bonus features included:

- Refresh token rotation
- Logout with token revocation
- Basic IP rate limiting on sensitive endpoints
- Structured request logging with request IDs

## How to Run the Project

1. **Create Virtual Environment & Install Dependencies:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Create `.env` file:**

```env
SECRET_KEY=replace-with-a-strong-secret
```

3. **Start the Application:**

```bash
uvicorn app.main:app --reload
```

4. **View API Documentation:**
   Open your browser and navigate to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Documentation

- `POST /register`: Accepts `name`, `email`, and `password`. Hashes password and creates user.
- `POST /login`: Accepts `email`, `password`. Validates credentials and returns access + refresh token.
- `POST /refresh`: Accepts a refresh token and returns a rotated token pair.
- `POST /logout`: Requires bearer token and revokes stored refresh token.
- `GET /me`: Requires `Authorization: Bearer <token>`. Returns current logged-in user profile.
- `DELETE /delete-account`: Requires bearer token. Deletes current authenticated account.
- `POST /send-code`: Takes `email`, generates and stores a 6-digit verification code (email send is simulated).
- `POST /verify`: Takes `email` and `code`, validates code, marks account as verified.

## Rate Limits

- `POST /register`: 10 requests/minute/IP
- `POST /login`: 10 requests/minute/IP
- `POST /send-code`: 5 requests/minute/IP

## Request Logging

- Each request is logged with `request_id`, method, path, status, and duration.
- Responses include `X-Request-ID` header.

### Example Request Bodies

`POST /register`

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "StrongPassword123"
}
```

`POST /login`

```json
{
  "email": "jane@example.com",
  "password": "StrongPassword123"
}
```

`POST /refresh`

```json
{
  "refresh_token": "<refresh-token-from-login>"
}
```

`POST /send-code`

```json
{
  "email": "jane@example.com"
}
```

`POST /verify`

```json
{
  "email": "jane@example.com",
  "code": "123456"
}
```

## Docker

Build and run:

```bash
docker build -t fastapi-auth-api .
docker run --rm -p 8000:8000 --env SECRET_KEY=replace-with-a-strong-secret fastapi-auth-api
```

Or run with Compose:

```bash
docker compose up --build
```
