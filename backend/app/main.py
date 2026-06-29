import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import auth, customers, dashboard, notifications, reports, tickets
from .seed import seed_default_users, seed_sample_customers, seed_sample_tickets


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_users(db)
        seed_sample_customers(db)
        seed_sample_tickets(db)
    yield


app = FastAPI(
    title="TechServe AI CRM API",
    description="CRM and ticket management MVP for TechServe Solutions.",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/api" if os.getenv("VERCEL") else "",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(tickets.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"message": "TechServe AI CRM API is running"}

@app.get("/setup")
def setup_database() -> dict[str, str]:
    """Manually trigger database setup for Serverless environments (which skip lifespan)."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_users(db)
        seed_sample_customers(db)
        seed_sample_tickets(db)
    return {"message": "Database tables created and default data seeded successfully!"}
