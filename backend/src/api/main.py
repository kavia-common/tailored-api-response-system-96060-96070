import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.routers import auth as auth_router
from src.api.routers import dashboard as dashboard_router
from src.api.routers import package as package_router
from src.api.routers import account as account_router

# App metadata for OpenAPI
openapi_tags = [
    {"name": "Authentication", "description": "User signup and login endpoints issuing JWTs"},
    {"name": "Dashboard", "description": "User/package dashboard endpoints"},
    {"name": "Tailored API", "description": "APIs that tailor responses based on user package tier"},
    {"name": "Account", "description": "Endpoints for user account operations like viewing/updating plan/package"},
]

app = FastAPI(
    title="TATA ELXSI MOCK API",
    description=(
        "TATA ELXSI MOCK API - A mock backend that issues JWT tokens and returns "
        "responses tailored to each user's subscription package."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS and environment configuration
# Load variables from .env if present (useful in dev/preview environments)
load_dotenv()

cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
allow_origins: List[str] = []

if cors_origins_env:
    # Comma-separated list of origins
    allow_origins = [o.strip().rstrip("/") for o in cors_origins_env.split(",") if o.strip()]
else:
    # Fallback to common frontend/site URL env vars if provided
    possible_vars = [
        "FRONTEND_ORIGIN",
        "FRONTEND_URL",
        "SITE_URL",
        "PUBLIC_SITE_URL",
        "REACT_APP_SITE_URL",
        "VITE_SITE_URL",
    ]
    for var in possible_vars:
        v = os.getenv(var)
        if v and v.strip():
            allow_origins.append(v.strip().rstrip("/"))
    # Last resort for open development; prefer explicit origins in production
    if not allow_origins:
        allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Dashboard"], summary="Health check")
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy"}


# Register routers
app.include_router(auth_router.router)
app.include_router(dashboard_router.router)
app.include_router(package_router.router)
app.include_router(account_router.router)
