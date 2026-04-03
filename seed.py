"""
Seed script - creates test users and sample transactions.
Run with: python seed.py
"""
import random
from datetime import date, timedelta

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.core.security import hash_password

USERS = [
    {"name": "Alice Admin", "email": "alice@mydb.dev", "password": "admin123", "role": UserRole.admin},
    {"name": "Arjun Analyst", "email": "arjun@mydb.dev", "password": "analyst123", "role": UserRole.analyst},
    {"name": "Vani Viewer", "email": "vani@mydb.dev", "password": "viewer123", "role": UserRole.viewer},
]

SAMPLE_TRANSACTIONS = [
    {"amount": 85000, "type": TransactionType.income, "category": "salary", "notes": "Monthly salary"},
    {"amount": 12000, "type": TransactionType.income, "category": "freelance", "notes": "Website project"},
    {"amount": 3500, "type": TransactionType.expense, "category": "rent", "notes": "Monthly rent"},
    {"amount": 800, "type": TransactionType.expense, "category": "groceries", "notes": None},
    {"amount": 2200, "type": TransactionType.expense, "category": "utilities", "notes": "Electricity + internet"},
    {"amount": 1500, "type": TransactionType.expense, "category": "transport", "notes": "Fuel and cab"},
    {"amount": 5000, "type": TransactionType.income, "category": "investments", "notes": "Dividend payout"},
    {"amount": 900, "type": TransactionType.expense, "category": "food", "notes": "Dining out"},
    {"amount": 3000, "type": TransactionType.expense, "category": "subscriptions", "notes": "SaaS tools"},
    {"amount": 15000, "type": TransactionType.income, "category": "bonus", "notes": "Q4 performance bonus"},
]


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        created_users = []
        for u in USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            created_users.append(user)

        db.commit()
        for u in created_users:
            db.refresh(u)

        analyst = next(u for u in created_users if u.role == UserRole.analyst)
        admin = next(u for u in created_users if u.role == UserRole.admin)

        today = date.today()
        for i in range(40):
            txn_data = random.choice(SAMPLE_TRANSACTIONS)
            days_ago = random.randint(0, 180)
            owner = random.choice([analyst, admin])

            txn = Transaction(
                amount=round(txn_data["amount"] + random.uniform(-500, 500), 2),
                type=txn_data["type"],
                category=txn_data["category"],
                date=today - timedelta(days=days_ago),
                notes=txn_data["notes"],
                created_by=owner.id,
            )
            db.add(txn)

        db.commit()
        print("Seeded 3 users and 40 transactions successfully.\n")
        print("Test credentials:")
        for u in USERS:
            print(f"  [{u['role'].value}] {u['email']} / {u['password']}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
