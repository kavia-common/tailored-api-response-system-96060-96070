import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import auth as auth_router
from src.api.routers import dashboard as dashboard_router
from src.api.routers import package as package_router

# App metadata for OpenAPI
openapi_tags = [
    {"name": "Authentication", "description": "User signup and login endpoints issuing JWTs"},
    {"name": "Dashboard", "description": "User/package dashboard endpoints"},
    {"name": "Tailored API", "description": "APIs that tailor responses based on user package tier"},
]

app = FastAPI(
    title="Tailored API Response Backend",
    description=(
        "Backend service that issues JWT tokens and returns responses tailored "
        "to each user's subscription package."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS configuration from env
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
allow_origins: List[str]
if cors_origins_env.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

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
