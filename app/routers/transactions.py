from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_analyst_or_admin, get_current_user, get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import transactions as txn_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    return txn_service.create_transaction(data, current_user, db)


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    type: TransactionType | None = Query(None),
    category: str | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_admin),
):
    filters = TransactionFilters(
        type=type,
        category=category,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit,
    )
    return txn_service.get_transactions(filters, db)


@router.get("/{txn_id}", response_model=TransactionResponse)
def get_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_admin),
):
    return txn_service.get_transaction_by_id(txn_id, db)


@router.patch("/{txn_id}", response_model=TransactionResponse)
def update_transaction(
    txn_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    return txn_service.update_transaction(txn_id, data, current_user, db)


@router.delete("/{txn_id}")
def delete_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return txn_service.delete_transaction(txn_id, current_user, db)
