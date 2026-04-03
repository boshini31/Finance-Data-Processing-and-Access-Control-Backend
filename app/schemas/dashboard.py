from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_transactions: int


class CategoryTotal(BaseModel):
    category: str
    total: float
    count: int


class MonthlyTrend(BaseModel):
    month: str
    income: float
    expenses: float


class RecentTransaction(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: str
    notes: str | None


class CategoryBreakdownResponse(BaseModel):
    income: list[CategoryTotal]
    expenses: list[CategoryTotal]


class RecentActivityResponse(BaseModel):
    transactions: list[RecentTransaction]
