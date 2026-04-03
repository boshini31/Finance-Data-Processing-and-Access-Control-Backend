from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import can_modify_transaction, can_delete_transaction
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionFilters, TransactionUpdate


def create_transaction(data: TransactionCreate, current_user: User, db: Session) -> Transaction:
    txn = Transaction(
        amount=data.amount,
        type=data.type,
        category=data.category.lower(),
        date=data.date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_transactions(filters: TransactionFilters, db: Session) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.is_deleted == False)  # noqa: E712

    if filters.type:
        query = query.filter(Transaction.type == filters.type)
    if filters.category:
        query = query.filter(Transaction.category == filters.category.lower())
    if filters.from_date:
        query = query.filter(Transaction.date >= filters.from_date)
    if filters.to_date:
        query = query.filter(Transaction.date <= filters.to_date)

    offset = (filters.page - 1) * filters.limit
    return query.order_by(Transaction.date.desc()).offset(offset).limit(filters.limit).all()


def get_transaction_by_id(txn_id: int, db: Session) -> Transaction:
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.is_deleted == False  # noqa: E712
    ).first()
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


def update_transaction(
    txn_id: int, data: TransactionUpdate, current_user: User, db: Session
) -> Transaction:
    txn = get_transaction_by_id(txn_id, db)
    can_modify_transaction(current_user, txn.created_by)

    if data.amount is not None:
        txn.amount = data.amount
    if data.type is not None:
        txn.type = data.type
    if data.category is not None:
        txn.category = data.category.lower()
    if data.date is not None:
        txn.date = data.date
    if data.notes is not None:
        txn.notes = data.notes

    db.commit()
    db.refresh(txn)
    return txn


def delete_transaction(txn_id: int, current_user: User, db: Session) -> dict:
    can_delete_transaction(current_user)
    txn = get_transaction_by_id(txn_id, db)
    txn.is_deleted = True
    db.commit()
    return {"message": f"Transaction {txn_id} deleted"}
