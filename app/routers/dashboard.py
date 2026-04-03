from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_any_role, get_db
from app.models.user import User
from app.schemas.dashboard import (
    CategoryBreakdownResponse,
    RecentActivityResponse,
    SummaryResponse,
    MonthlyTrend,
)
from app.services import dashboard as dash_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    return dash_service.get_summary(db)


@router.get("/by-category", response_model=CategoryBreakdownResponse)
def by_category(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    return dash_service.get_category_breakdown(db)


@router.get("/monthly-trends", response_model=list[MonthlyTrend])
def monthly_trends(
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    return dash_service.get_monthly_trends(db)


@router.get("/recent", response_model=RecentActivityResponse)
def recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    return dash_service.get_recent_activity(db, limit)
