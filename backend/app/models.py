from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('manager', 'agent')", name="ck_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="agent")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    assigned_customers: Mapped[list["Customer"]] = relationship(back_populates="assigned_agent")
    assigned_tickets: Mapped[list["Ticket"]] = relationship(back_populates="assigned_agent")
    comments: Mapped[list["TicketComment"]] = relationship(back_populates="agent")
    activities: Mapped[list["TicketActivity"]] = relationship(back_populates="actor")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    assigned_agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    assigned_agent: Mapped[User | None] = relationship(back_populates="assigned_customers")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="customer")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(240), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Open", index=True)
    priority: Mapped[str] = mapped_column(String(30), default="Medium", index=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    assigned_agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ai_sentiment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="tickets")
    assigned_agent: Mapped[User | None] = relationship(back_populates="assigned_tickets")
    comments: Mapped[list["TicketComment"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    activities: Mapped[list["TicketActivity"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["NotificationLog"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    ticket: Mapped[Ticket] = relationship(back_populates="comments")
    agent: Mapped[User] = relationship(back_populates="comments")


class TicketActivity(Base):
    __tablename__ = "ticket_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    ticket: Mapped[Ticket] = relationship(back_populates="activities")
    actor: Mapped[User] = relationship(back_populates="activities")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    platform: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    ticket: Mapped[Ticket] = relationship(back_populates="notifications")
