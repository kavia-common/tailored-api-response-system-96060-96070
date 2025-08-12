from fastapi import APIRouter, HTTPException, status

from src.api.models import SignupRequest, LoginRequest, TokenResponse, PackageTier
from src.api.storage import db
from src.api.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# PUBLIC_INTERFACE
@router.post(
    "/signup",
    response_model=TokenResponse,
    summary="Create account and issue token",
    description="Registers a new user with optional package tier (defaults to 'free') and returns a JWT access token.",
    responses={
        201: {"description": "User created; token issued"},
        400: {"description": "Email already exists"},
    },
    status_code=201,
)
def signup(payload: SignupRequest) -> TokenResponse:
    """Register a new user and return an access token."""
    existing = db.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    tier = payload.package_tier or PackageTier.free
    record = db.create_user(email=str(payload.email), password=payload.password, package_tier=tier)

    token = create_access_token(subject=record["id"], additional_claims={"pkg": record["package_tier"]})
    return TokenResponse(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and issue token",
    description="Authenticates a user with email/password and returns a JWT access token.",
    responses={
        200: {"description": "Authenticated; token issued"},
        401: {"description": "Invalid credentials"},
    },
)
def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate an existing user and return an access token."""
    record = db.verify_password(email=str(payload.email), password=payload.password)
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(subject=record["id"], additional_claims={"pkg": record["package_tier"]})
    return TokenResponse(access_token=token, token_type="bearer")
