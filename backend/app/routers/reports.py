from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies import require_manager
from ..models import Customer, Ticket, User

router = APIRouter(prefix="/reports", tags=["reports"])

TICKET_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
TICKET_PRIORITIES = ("Low", "Medium", "High", "Critical")


def _count_values(values: list[str], labels: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(values)
    return {label: counts.get(label, 0) for label in labels}


def _category(ticket: Ticket) -> str:
    return ticket.category or ticket.ai_category or "Uncategorized"


@router.get("/summary", response_model=schemas.ReportSummary)
def get_report_summary(
    _: User = Depends(require_manager), db: Session = Depends(get_db)
) -> schemas.ReportSummary:
    tickets = list(db.scalars(select(Ticket)).all())
    agent_names = {
        user.id: user.name for user in db.scalars(select(User).where(User.role == "agent")).all()
    }
    resolution_hours = [
        (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
        for ticket in tickets
        if ticket.resolved_at
    ]
    resolved_tickets = sorted(
        (ticket for ticket in tickets if ticket.resolved_at),
        key=lambda ticket: ticket.resolved_at,
        reverse=True,
    )
    return schemas.ReportSummary(
        total_tickets=len(tickets),
        total_customers=db.scalar(select(func.count()).select_from(Customer)) or 0,
        ticket_count_by_category=dict(sorted(Counter(_category(ticket) for ticket in tickets).items())),
        ticket_count_by_status=_count_values([ticket.status for ticket in tickets], TICKET_STATUSES),
        ticket_count_by_priority=_count_values([ticket.priority for ticket in tickets], TICKET_PRIORITIES),
        ticket_count_by_agent=dict(
            Counter(agent_names.get(ticket.assigned_agent_id, "Unassigned") for ticket in tickets)
        ),
        resolved_tickets=len(resolved_tickets),
        average_resolution_time_hours=(
            round(sum(resolution_hours) / len(resolution_hours), 2) if resolution_hours else None
        ),
        critical_tickets=sum(ticket.priority == "Critical" for ticket in tickets),
        recent_resolved_tickets=[
            schemas.RecentResolvedTicket(
                id=ticket.id,
                title=ticket.title,
                category=_category(ticket),
                priority=ticket.priority,
                customer_name=ticket.customer.full_name,
                assigned_agent_name=ticket.assigned_agent.name if ticket.assigned_agent else None,
                resolved_at=ticket.resolved_at,
            )
            for ticket in resolved_tickets[:5]
        ],
    )
