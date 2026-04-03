from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip().lower()


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v is not None else None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: str 
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilters(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    page: int = 1
    limit: int = 20

    @field_validator("limit")
    @classmethod
    def limit_cap(cls, v: int) -> int:
        return min(v, 100)
