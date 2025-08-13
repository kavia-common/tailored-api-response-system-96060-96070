from fastapi import APIRouter, HTTPException, status, Form

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
def login(
    payload: LoginRequest | None = None,
    email: str | None = Form(
        default=None,
        description="Email for account login when using form-encoded payloads (alias of 'username').",
    ),
    password: str | None = Form(
        default=None,
        description="Password for account login when using form-encoded payloads.",
    ),
    username: str | None = Form(
        default=None,
        description="Alias used by OAuth2PasswordRequestForm; treated as the email.",
    ),
) -> TokenResponse:
    """Authenticate an existing user and return an access token.

    Supports both application/json (LoginRequest) and application/x-www-form-urlencoded
    with fields 'email' or 'username' and 'password'. This improves compatibility with
    various frontend/client implementations that may post form data instead of JSON.
    """
    # Determine credentials source: JSON payload or form fields
    json_email = str(payload.email) if payload and getattr(payload, "email", None) else None
    json_password = payload.password if payload and getattr(payload, "password", None) else None

    form_email = email or username
    form_password = password

    final_email = json_email or form_email
    final_password = json_password or form_password

    if not final_email or not final_password:
        # Let FastAPI return 422 for missing fields or provide a clear error
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email/username and password are required",
        )

    record = db.verify_password(email=str(final_email), password=final_password)
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=record["id"], additional_claims={"pkg": record["package_tier"]})
    return TokenResponse(access_token=token, token_type="bearer")


# Add a trailing-slash alias for clients that may post to '/auth/login/'
router.add_api_route(
    "/login/",
    login,
    methods=["POST"],
    include_in_schema=False,
    summary="Login and issue token (alias with trailing slash)",
    description="Alias for /auth/login to improve client compatibility.",
)
