from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user
from src.api.models import DashboardResponse, DashboardFeature, UserPublic, PackageTier

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _features_for(tier: PackageTier) -> list[DashboardFeature]:
    base = [
        DashboardFeature(key="basic_data", label="Basic Data", enabled=True),
        DashboardFeature(key="support", label="Community Support", enabled=True),
    ]
    if tier in (PackageTier.pro, PackageTier.enterprise):
        base.append(DashboardFeature(key="pro_data", label="Pro Data", enabled=True, limit=10000))
        base.append(DashboardFeature(key="priority_support", label="Priority Support", enabled=True))
    if tier is PackageTier.enterprise:
        base.append(DashboardFeature(key="enterprise_data", label="Enterprise Data", enabled=True, limit=100000))
        base.append(DashboardFeature(key="analytics", label="Advanced Analytics", enabled=True))
        base.append(DashboardFeature(key="sla", label="Enterprise SLA", enabled=True))
    return base


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=DashboardResponse,
    summary="Get dashboard info",
    description="Returns the authenticated user's profile and features enabled by their package tier.",
)
def me(user: UserPublic = Depends(get_current_user)) -> DashboardResponse:
    """Return user profile and feature entitlements for their package tier."""
    return DashboardResponse(user=user, features=_features_for(user.package_tier))
