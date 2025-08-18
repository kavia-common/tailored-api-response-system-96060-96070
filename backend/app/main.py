import os
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from .schemas import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserPublic,
    DashboardFeature,
    DashboardResponse,
    PlanInfo,
    PlanUpdateRequest,
    TailoredContentResponse,
)
from .storage import MemoryUserStore, UserRecord
from .security import create_access_token, get_current_user, store_singleton


def _parse_cors_origins() -> List[str]:
    """
    Parse allowed origins from the environment:
    - BACKEND_CORS_ORIGINS: comma-separated list of origins
    - FRONTEND_ORIGIN: single origin
    Combines both if provided and removes duplicates/empties.
    """
    origins: List[str] = []
    raw_list = os.environ.get("BACKEND_CORS_ORIGINS", "")
    if raw_list:
        origins.extend([o.strip() for o in raw_list.split(",") if o.strip()])
    single = os.environ.get("FRONTEND_ORIGIN", "").strip()
    if single:
        origins.append(single)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for o in origins:
        if o not in seen:
            seen.add(o)
            result.append(o)
    # If none provided, default to allowing all for development convenience
    return result or ["*"]


openapi_tags = [
    {"name": "Authentication", "description": "User signup and login endpoints issuing JWTs"},
    {"name": "Dashboard", "description": "User/package dashboard endpoints"},
    {"name": "Tailored API", "description": "APIs that tailor responses based on user package tier"},
    {"name": "Account", "description": "Endpoints for user account operations like viewing/updating plan/package"},
]

APP_NAME = os.environ.get("APP_NAME", "TATA ELXSI MOCK API")

app = FastAPI(
    title=APP_NAME,
    description="TATA ELXSI MOCK API - A mock backend that issues JWT tokens and returns responses tailored to each user's subscription package.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _features_for_tier(tier: str) -> List[DashboardFeature]:
    tier = (tier or "").lower().strip()
    base = [
        DashboardFeature(key="basic-search", label="Basic Search", enabled=True, limit=100),
        DashboardFeature(key="reports", label="Reports", enabled=tier in {"pro", "enterprise"}, limit=10 if tier == "pro" else (50 if tier == "enterprise" else None)),
        DashboardFeature(key="export", label="Data Export", enabled=tier in {"pro", "enterprise"}),
        DashboardFeature(key="analytics", label="Advanced Analytics", enabled=tier == "enterprise"),
    ]
    # Add a synthetic per-tier marker feature
    base.append(DashboardFeature(key=f"tier-{tier or 'free'}", label=f"Tier: {tier or 'free'}", enabled=True))
    return base


def _public_user(user: UserRecord) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, package_tier=user.package_tier)


@app.get("/", tags=["Dashboard"], summary="Health check", description="Simple health check endpoint.")
def health_check():
    """
    PUBLIC_INTERFACE
    Health check API.

    Returns:
        JSON with service status and name.
    """
    return {"status": "ok", "service": APP_NAME}


@app.post(
    "/auth/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Create account and issue token",
    description="Registers a new user with optional package tier (defaults to 'free') and returns a JWT access token.",
)
def signup(payload: SignupRequest, store: MemoryUserStore = Depends(lambda: store_singleton)):
    """
    PUBLIC_INTERFACE
    Signup endpoint.

    Parameters:
        payload (SignupRequest): Email, password, optional package_tier.

    Returns:
        TokenResponse: Access token and type.

    Raises:
        400 if email already exists.
        422 if validation fails.
    """
    try:
        user = store.create_user(
            email=payload.email,
            password_plain=payload.password,
            package_tier=(payload.package_tier or "free").lower(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    token = create_access_token(user=user)
    return TokenResponse(access_token=token)


@app.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Login and issue token",
    description="Authenticates a user with email/password and returns a JWT access token.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    # Optional explicit fields for compatibility with clients posting 'email' in form
    email: Optional[str] = Form(default=None, description="Email for account login when using form-encoded payloads (alias of 'username')."),
    password: Optional[str] = Form(default=None, description="Password for account login when using form-encoded payloads."),
    store: MemoryUserStore = Depends(lambda: store_singleton),
):
    """
    PUBLIC_INTERFACE
    Login endpoint.

    Accepts both OAuth2 'username' field and an 'email' alias for convenience.

    Returns:
        TokenResponse on success.

    Raises:
        401 if credentials are invalid.
    """
    submitted_email = email or form_data.username
    submitted_pwd = password or form_data.password
    user = store.authenticate(submitted_email, submitted_pwd)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user=user)
    return TokenResponse(access_token=token)


@app.get(
    "/dashboard/me",
    response_model=DashboardResponse,
    tags=["Dashboard"],
    summary="Get dashboard info",
    description="Returns the authenticated user's profile and features enabled by their package tier.",
)
def me(current_user: UserRecord = Depends(get_current_user)):
    """
    PUBLIC_INTERFACE
    Get current user's dashboard data.

    Returns:
        DashboardResponse: profile + features array.
    """
    features = _features_for_tier(current_user.package_tier)
    return DashboardResponse(user=_public_user(current_user), features=features)


@app.get(
    "/api/content",
    response_model=TailoredContentResponse,
    tags=["Tailored API"],
    summary="Get tailored content",
    description="Returns content whose fields and richness depend on the requesting user's package tier.",
)
def get_content(current_user: UserRecord = Depends(get_current_user)):
    """
    PUBLIC_INTERFACE
    Tailored content API. The content returned depends on the user's package.

    Returns:
        TailoredContentResponse with fields varying per package tier.
    """
    tier = (current_user.package_tier or "free").lower()
    base = {
        "summary": f"Content for {tier} user",
        "data_basic": ["overview", "getting-started", "samples"],
        "data_pro": None,
        "data_enterprise": None,
        "analytics": None,
    }
    if tier in {"pro", "enterprise"}:
        base["data_pro"] = ["pro-tips", "enhanced-datasets"]
    if tier == "enterprise":
        base["data_enterprise"] = ["enterprise-insights", "priority-roadmap"]
        base["analytics"] = {"dashboards": 5, "pipeline": "real-time", "sla": "99.9%"}
    return TailoredContentResponse(**base)  # type: ignore[arg-type]


@app.get(
    "/account/plan",
    response_model=PlanInfo,
    tags=["Account"],
    summary="Get current user's plan",
    description="Returns the authenticated user's current subscription package tier.",
)
def get_plan(current_user: UserRecord = Depends(get_current_user)):
    """
    PUBLIC_INTERFACE
    Get the authenticated user's current plan.

    Returns:
        PlanInfo with package_tier.
    """
    return PlanInfo(package_tier=current_user.package_tier)


class _PlanUpdateResponse(BaseModel):
    package_tier: str


@app.put(
    "/account/plan",
    response_model=PlanInfo,
    tags=["Account"],
    summary="Update current user's plan",
    description="Updates the authenticated user's subscription package tier. Returns the new plan. Clients should re-fetch any package-tailored data after this change.",
)
def update_plan(payload: PlanUpdateRequest, current_user: UserRecord = Depends(get_current_user), store: MemoryUserStore = Depends(lambda: store_singleton)):
    """
    PUBLIC_INTERFACE
    Update the authenticated user's plan/package.

    Parameters:
        payload (PlanUpdateRequest): New package tier (free|pro|enterprise).

    Returns:
        PlanInfo: Updated plan.

    Raises:
        400 if package is invalid.
    """
    new_tier = (payload.package_tier or "").lower().strip()
    if new_tier not in {"free", "pro", "enterprise"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")
    updated = store.update_plan(current_user.id, new_tier)
    if not updated:
        # Should not happen unless user disappeared from store
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return PlanInfo(package_tier=updated.package_tier)
