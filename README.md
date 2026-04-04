# FastAPI Authentication API

Backend task for building an Authentication System using FastAPI and SQLite.

## Overview
This API provides a complete authentication flow for frontend and mobile developers:
- Register users with hashed passwords
- Login with JWT generation
- Get logged-in user details
- Delete accounts
- Example Email Verification simulation (Generating 6-digit code and validating it)

## How to Run the Project

1. **Create Virtual Environment & Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Setup the Environment file:**
   Update the `.env` file if necessary. A default `.env` is already configured for SQLite.

3. **Start the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **View API Documentation:**
   Open your browser and navigate to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   This Swagger UI lets you directly interact with all the API endpoints.

## API Documentation

- `POST /register`: Accepts `name`, `email`, and `password`. Hashes password and saves to DB.
- `POST /login`: Accepts `email`, `password`. Validates and returns a JWT token.
- `GET /me`: Requires `Bearer <token>`. Returns current logged-in user profile.
- `DELETE /delete-account`: Requires `Bearer <token>`. Deletes the user profile.
- `POST /send-code`: Takes `email`, generates a 6-digit verification code. (Simulates sending an email)
- `POST /verify`: Takes `email` and 6-digit `code`, and marks the user account as verified.
