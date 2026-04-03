from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, transactions, dashboard

app = FastAPI(
    title="mydb Dashboard API",
    description="Backend API for managing financial records with role-based access control.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "mydb API is running"}
