# Tailored API Response Backend (FastAPI)

A FastAPI backend that issues JWT tokens, manages simple in-memory users and subscription packages, and tailors all API responses based on the authenticated user's package tier.

Features:
- User signup and login with JWT authentication
- Package-aware dashboard and API content
- Update and retrieve current user's plan
- Robust CORS configured via environment variables
- Rich OpenAPI/Swagger documentation

## Quick start

1. Install dependencies
   pip install -r requirements.txt

2. Set environment variables (see .env.example for guidance). At minimum:
   - JWT_SECRET_KEY
   - BACKEND_CORS_ORIGINS or FRONTEND_ORIGIN

3. Run the server
   uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

4. Open docs
   http://localhost:3001/docs

## Environment variables

Do not commit secrets. Provide the following via environment or deployment configuration.

- JWT_SECRET_KEY: Secret used for signing JWT access tokens.
- JWT_ALGORITHM: Algorithm for JWT signing (default: HS256).
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry in minutes (default: 1440 = 24 hours).
- BACKEND_CORS_ORIGINS: Comma-separated list of allowed origins for CORS (example: http://localhost:3000,https://myapp.com).
- FRONTEND_ORIGIN: Single frontend origin. If both BACKEND_CORS_ORIGINS and FRONTEND_ORIGIN are provided, both are allowed.
- APP_NAME: Optional FastAPI title override.

## Notes

- This app uses an in-memory store for users; it is suitable for demos and local development only. For production, replace the storage with a database.
- The OpenAPI shows OAuth2 password flow; the token endpoint is /auth/login.
- When using form-encoded login, either username or email (aliases) may be provided.
