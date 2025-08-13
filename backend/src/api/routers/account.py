from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user
from src.api.models import UserPublic, PackageTier, PlanInfo, PlanUpdateRequest
from src.api.storage import db

router = APIRouter(prefix="/account", tags=["Account"])


# PUBLIC_INTERFACE
@router.get(
    "/plan",
    response_model=PlanInfo,
    summary="Get current user's plan",
    description="Returns the authenticated user's current subscription package tier.",
    responses={
        200: {"description": "Current plan retrieved"},
        401: {"description": "Unauthorized"},
    },
)
def get_plan(user: UserPublic = Depends(get_current_user)) -> PlanInfo:
    """Return the current authenticated user's package tier."""
    return PlanInfo(package_tier=user.package_tier)


# PUBLIC_INTERFACE
@router.put(
    "/plan",
    response_model=PlanInfo,
    summary="Update current user's plan",
    description=(
        "Updates the authenticated user's subscription package tier. "
        "Returns the new plan. Clients should re-fetch any package-tailored data after this change."
    ),
    responses={
        200: {"description": "Plan updated successfully"},
        400: {"description": "Invalid plan"},
        401: {"description": "Unauthorized"},
    },
)
def update_plan(payload: PlanUpdateRequest, user: UserPublic = Depends(get_current_user)) -> PlanInfo:
    """Update the current user's package tier and return the updated plan."""
    updated = db.set_package(user_id=user.id, package_tier=payload.package_tier)
    if not updated:
        # This should not occur under normal conditions since the user comes from a verified token
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return PlanInfo(package_tier=PackageTier(updated["package_tier"]))
