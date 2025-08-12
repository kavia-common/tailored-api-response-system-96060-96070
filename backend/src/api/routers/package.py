from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user
from src.api.models import TailoredContentResponse, UserPublic, PackageTier

router = APIRouter(prefix="/api", tags=["Tailored API"])


# PUBLIC_INTERFACE
@router.get(
    "/content",
    response_model=TailoredContentResponse,
    summary="Get tailored content",
    description="Returns content whose fields and richness depend on the requesting user's package tier.",
)
def get_content(user: UserPublic = Depends(get_current_user)) -> TailoredContentResponse:
    """Return content shaped according to the user's package tier."""
    basic = ["item-a", "item-b", "item-c"]
    if user.package_tier == PackageTier.free:
        return TailoredContentResponse(
            summary="Basic content for Free tier",
            data_basic=basic,
        )
    if user.package_tier == PackageTier.pro:
        return TailoredContentResponse(
            summary="Expanded content for Pro tier",
            data_basic=basic,
            data_pro=["pro-x", "pro-y", "pro-z"],
        )
    # Enterprise
    return TailoredContentResponse(
        summary="Full content and analytics for Enterprise tier",
        data_basic=basic,
        data_pro=["pro-x", "pro-y", "pro-z"],
        data_enterprise=["ent-1", "ent-2", "ent-3"],
        analytics={"insights": {"score": 92, "segments": ["alpha", "beta"]}},
    )
