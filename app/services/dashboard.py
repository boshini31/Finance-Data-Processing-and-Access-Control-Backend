from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.dashboard import (
    SummaryResponse,
    CategoryTotal,
    CategoryBreakdownResponse,
    MonthlyTrend,
    RecentActivityResponse,
    RecentTransaction,
)


def _active(db: Session):
    return db.query(Transaction).filter(Transaction.is_deleted == False)  # noqa: E712


def get_summary(db: Session) -> SummaryResponse:
    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,  # noqa: E712
        Transaction.type == TransactionType.income,
    ).scalar() or 0.0

    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,  # noqa: E712
        Transaction.type == TransactionType.expense,
    ).scalar() or 0.0

    total = _active(db).count()

    return SummaryResponse(
        total_income=round(income, 2),
        total_expenses=round(expenses, 2),
        net_balance=round(income - expenses, 2),
        total_transactions=total,
    )


def get_category_breakdown(db: Session) -> CategoryBreakdownResponse:
    rows = (
        db.query(
            Transaction.category,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.is_deleted == False)  # noqa: E712
        .group_by(Transaction.category, Transaction.type)
        .all()
    )

    income_cats = []
    expense_cats = []

    for row in rows:
        entry = CategoryTotal(category=row.category, total=round(row.total, 2), count=row.count)
        if row.type == TransactionType.income:
            income_cats.append(entry)
        else:
            expense_cats.append(entry)

    return CategoryBreakdownResponse(income=income_cats, expenses=expense_cats)


def get_monthly_trends(db: Session) -> list[MonthlyTrend]:
    year_col = extract("year", Transaction.date).label("year")
    month_col = extract("month", Transaction.date).label("month")

    rows = (
        db.query(
            year_col,
            month_col,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(Transaction.is_deleted == False)  # noqa: E712
        .group_by(year_col, month_col, Transaction.type)
        .order_by(year_col, month_col)
        .all()
    )

    trends: dict[str, dict] = {}
    for row in rows:
        key = f"{int(row.year)}-{int(row.month):02d}"
        if key not in trends:
            trends[key] = {"month": key, "income": 0.0, "expenses": 0.0}
        if row.type == TransactionType.income:
            trends[key]["income"] = round(row.total, 2)
        else:
            trends[key]["expenses"] = round(row.total, 2)

    return [MonthlyTrend(**v) for v in trends.values()]


def get_recent_activity(db: Session, limit: int = 10) -> RecentActivityResponse:
    txns = (
        _active(db)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )

    return RecentActivityResponse(
        transactions=[
            RecentTransaction(
                id=t.id,
                amount=t.amount,
                type=t.type.value,
                category=t.category,
                date=str(t.date),
                notes=t.notes,
            )
            for t in txns
        ]
    )
