from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import hash_password
from .models import Customer, Ticket, TicketActivity, User, utc_now
from .services import ai_service

DEFAULT_USERS = (
    {
        "name": "TechServe Manager",
        "email": "manager@example.com",
        "password": "password123",
        "role": "manager",
    },
    {
        "name": "Support Agent",
        "email": "agent@example.com",
        "password": "password123",
        "role": "agent",
    },
)

SAMPLE_CUSTOMERS = (
    {
        "full_name": "Ali Raza",
        "email": "ali.raza@example.com",
        "phone": "+92 300 1234567",
        "company": "TechServe Solutions",
        "notes": "Primary contact for internal technology support.",
        "assign_to_agent": True,
    },
    {
        "full_name": "Sara Khan",
        "email": "sara.khan@example.com",
        "phone": "+92 301 7654321",
        "company": "BrightSoft",
        "notes": "Software services customer.",
        "assign_to_agent": True,
    },
    {
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1 415 555 0147",
        "company": "CloudNova",
        "notes": "Cloud infrastructure account.",
        "assign_to_agent": True,
    },
    {
        "full_name": "Ayesha Malik",
        "email": "ayesha.malik@example.com",
        "phone": "+92 333 4567890",
        "company": "RetailPro",
        "notes": "Retail operations contact.",
        "assign_to_agent": False,
    },
    {
        "full_name": "Omar Farooq",
        "email": "omar.farooq@example.com",
        "phone": "+92 321 1112233",
        "company": "FinEdge",
        "notes": "Finance platform customer.",
        "assign_to_agent": False,
    },
)

SAMPLE_TICKETS = (
    {
        "title": "Cannot login to account",
        "description": "The customer cannot login after resetting their password and needs account access restored.",
        "category": "Account",
        "priority": "High",
        "status": "Open",
        "customer_email": "ali.raza@example.com",
        "assign_to_agent": True,
        "days_ago": 1,
    },
    {
        "title": "Billing invoice mismatch",
        "description": "The latest billing invoice contains an incorrect charge and needs review.",
        "category": "Billing",
        "priority": "Medium",
        "status": "In Progress",
        "customer_email": "sara.khan@example.com",
        "assign_to_agent": True,
        "days_ago": 2,
    },
    {
        "title": "Application crashes on dashboard",
        "description": "The application crashes with an error whenever the dashboard loads. This is urgent.",
        "category": "Technical",
        "priority": "Critical",
        "status": "Open",
        "customer_email": "john.smith@example.com",
        "assign_to_agent": True,
        "days_ago": 1,
    },
    {
        "title": "Need refund update",
        "description": "The customer requested an update about a refund for a duplicate payment.",
        "category": "Billing",
        "priority": "Low",
        "status": "Resolved",
        "customer_email": "ayesha.malik@example.com",
        "assign_to_agent": False,
        "days_ago": 4,
    },
    {
        "title": "Shipping tracking link not updating",
        "description": "The shipping tracking page has not updated the package delivery status.",
        "category": "Shipping",
        "priority": "Medium",
        "status": "Open",
        "customer_email": "omar.farooq@example.com",
        "assign_to_agent": False,
        "days_ago": 3,
    },
    {
        "title": "Profile company name correction",
        "description": "Please correct the company name shown on the customer account profile.",
        "category": "Account",
        "priority": "Low",
        "status": "Closed",
        "customer_email": "ali.raza@example.com",
        "assign_to_agent": True,
        "days_ago": 6,
    },
)


def seed_default_users(db: Session) -> None:
    for user_data in DEFAULT_USERS:
        existing = db.scalar(select(User).where(User.email == user_data["email"]))
        if existing:
            continue
        db.add(
            User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
        )
    db.commit()


def seed_sample_customers(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Customer)):
        return

    default_agent = db.scalar(select(User).where(User.email == "agent@example.com"))
    for customer_data in SAMPLE_CUSTOMERS:
        values = customer_data.copy()
        assign_to_agent = values.pop("assign_to_agent")
        db.add(
            Customer(
                **values,
                assigned_agent_id=default_agent.id if assign_to_agent and default_agent else None,
            )
        )
    db.commit()


def seed_sample_tickets(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Ticket)):
        return

    manager = db.scalar(select(User).where(User.email == "manager@example.com"))
    default_agent = db.scalar(select(User).where(User.email == "agent@example.com"))
    customers = {customer.email: customer for customer in db.scalars(select(Customer)).all()}
    if not manager or not customers:
        return

    for ticket_data in SAMPLE_TICKETS:
        values = ticket_data.copy()
        customer = customers.get(values.pop("customer_email"))
        if not customer:
            continue
        assign_to_agent = values.pop("assign_to_agent")
        days_ago = values.pop("days_ago")
        created_at = utc_now() - timedelta(days=days_ago)
        resolved_at = created_at + timedelta(hours=6) if values["status"] == "Resolved" else None
        ticket = Ticket(
            **values,
            customer_id=customer.id,
            assigned_agent_id=default_agent.id if assign_to_agent and default_agent else None,
            created_at=created_at,
            updated_at=resolved_at or created_at,
            resolved_at=resolved_at,
            ai_category=ai_service.classify_ticket(values["title"], values["description"]),
            ai_sentiment=ai_service.analyze_sentiment(values["title"], values["description"]),
            ai_summary="Refund update reviewed and resolved." if values["status"] == "Resolved" else None,
        )
        db.add(ticket)
        db.flush()
        db.add(
            TicketActivity(
                ticket_id=ticket.id,
                actor_id=manager.id,
                action="Ticket created",
                old_value=None,
                new_value=ticket.status,
                created_at=created_at,
            )
        )
        if ticket.status == "Resolved":
            db.add(
                TicketActivity(
                    ticket_id=ticket.id,
                    actor_id=manager.id,
                    action="Ticket resolved",
                    old_value="In Progress",
                    new_value=ticket.status,
                    created_at=resolved_at,
                )
            )
        elif ticket.status == "Closed":
            db.add(
                TicketActivity(
                    ticket_id=ticket.id,
                    actor_id=manager.id,
                    action="Ticket closed",
                    old_value="Resolved",
                    new_value=ticket.status,
                    created_at=created_at + timedelta(hours=8),
                )
            )
    db.commit()
