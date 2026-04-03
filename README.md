# Finance Dashboard Backend

A backend API for managing financial records with role-based access control, built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (via SQLAlchemy ORM) |
| Migrations | Alembic |
| Auth | JWT (PyJWT) + bcrypt password hashing |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## Features Implemented

### ✅ User & Role Management
- Register and login users with JWT-based authentication
- Three roles: **Viewer**, **Analyst**, **Admin**
- User activation/deactivation (is_active flag)
- Role-based middleware enforced at every endpoint

### ✅ Financial Records (Transactions)
- Full CRUD — Create, Read, Update, Delete
- Fields: `amount`, `type` (income/expense), `category`, `date`, `notes`
- **Soft delete** — records are flagged `is_deleted=true`, never hard deleted
- Filtering by `type`, `category`, `from_date`, `to_date`
- **Pagination** — configurable `page` and `limit` query params

### ✅ Dashboard Summary APIs
- `GET /dashboard/summary` — total income, total expenses, net balance, transaction count
- `GET /dashboard/by-category` — income and expense breakdown per category
- `GET /dashboard/monthly-trends` — month-wise income vs expense trends
- `GET /dashboard/recent` — latest N transactions (configurable limit)

### ✅ Access Control
Role-based guards enforced via FastAPI dependency injection:

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View dashboard summary | ✅ | ✅ | ✅ |
| View transactions | ❌ | ✅ | ✅ |
| Create transactions | ❌ | ✅ (own only) | ✅ |
| Update transactions | ❌ | ✅ (own only) | ✅ (any) |
| Delete transactions | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

### ✅ Validation & Error Handling
- Pydantic schemas validate all input fields
- Meaningful HTTP status codes (400, 401, 403, 404, 422)
- Descriptive error messages for all failure cases

---

## Project Structure

```
app/
├── core/
│   ├── dependencies.py   # Auth + role dependency injection
│   ├── permissions.py    # Fine-grained permission checks
│   └── security.py       # JWT creation & verification, password hashing
├── models/
│   ├── user.py           # User model with UserRole enum
│   └── transaction.py    # Transaction model with soft delete
├── routers/
│   ├── auth.py           # /auth/register, /auth/login, /auth/me
│   ├── users.py          # /users - admin user management
│   ├── transactions.py   # /transactions - CRUD + filters + pagination
│   └── dashboard.py      # /dashboard - summary, trends, categories
├── schemas/              # Pydantic request/response models
├── services/             # Business logic layer (separate from routers)
├── config.py             # Environment config via pydantic-settings
├── database.py           # SQLAlchemy session and Base
└── main.py               # App entry point with CORS middleware
migrations/               # Alembic migration files
seed.py                   # Script to seed sample data
```

---

## Setup & Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL running locally

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd finance-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/financedb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. (Optional) Seed sample data

```bash
python seed.py
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

API is now live at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

---

## API Overview

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current user info |

### Transactions
| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| POST | `/transactions/` | Create a transaction | Analyst, Admin |
| GET | `/transactions/` | List transactions (with filters + pagination) | Analyst, Admin |
| GET | `/transactions/{id}` | Get single transaction | Analyst, Admin |
| PATCH | `/transactions/{id}` | Update a transaction | Analyst (own), Admin |
| DELETE | `/transactions/{id}` | Soft delete a transaction | Admin only |

**Query params for listing:** `type`, `category`, `from_date`, `to_date`, `page`, `limit`

### Dashboard
| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/dashboard/summary` | Total income, expenses, net balance | All roles |
| GET | `/dashboard/by-category` | Income & expense breakdown by category | All roles |
| GET | `/dashboard/monthly-trends` | Month-wise income vs expense | All roles |
| GET | `/dashboard/recent` | Recent transactions (limit query param) | All roles |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/` | List all users |
| PATCH | `/users/{id}` | Update user role or status |

---

## Assumptions Made

1. **Viewers can see dashboard data** but cannot access raw transaction records. This simulates a dashboard-only user (e.g., a manager who sees summaries but not individual entries).
2. **Analysts own their transactions** — they can create and update only their own records. Admins can act on any.
3. **Soft delete only** — no transaction is ever permanently deleted. The `is_deleted` flag ensures auditability.
4. **PostgreSQL** is used as the primary database. SQLite can be substituted by changing `DATABASE_URL` in `.env`.
5. JWT tokens are stateless — no token blacklisting (logout simply means discarding the token client-side).

---

## Design Decisions

- **Separation of concerns**: Routers handle HTTP, Services handle business logic, Models handle data. No business logic lives in routers.
- **Dependency injection for auth**: FastAPI's `Depends()` is used to inject role checks at the router level, keeping access control declarative and visible.
- **Pydantic v2 schemas**: Separate schemas for Create, Update, and Response prevent accidental data leakage (e.g., hashed passwords never appear in responses).
- **Alembic migrations**: Schema changes are versioned and reproducible.
