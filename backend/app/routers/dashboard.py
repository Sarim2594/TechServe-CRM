from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies import require_agent_or_manager
from ..models import Customer, Ticket, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

TICKET_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
TICKET_PRIORITIES = ("Low", "Medium", "High", "Critical")


def _count_values(values: list[str], labels: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(values)
    return {label: counts.get(label, 0) for label in labels}


def _category(ticket: Ticket) -> str:
    return ticket.category or ticket.ai_category or "Uncategorized"


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(require_agent_or_manager), db: Session = Depends(get_db)
) -> schemas.DashboardStats:
    query = select(Ticket).order_by(Ticket.created_at.desc())
    customer_count_query = select(func.count()).select_from(Customer)
    if current_user.role == "agent":
        query = query.where(Ticket.assigned_agent_id == current_user.id)
        customer_count_query = customer_count_query.where(Customer.assigned_agent_id == current_user.id)
    tickets = list(db.scalars(query).all())
    today = date.today()

    agents_query = select(User).where(User.role == "agent", User.is_active.is_(True)).order_by(User.name)
    if current_user.role == "agent":
        agents_query = agents_query.where(User.id == current_user.id)
    agents = db.scalars(agents_query).all()
    workloads = [
        schemas.AgentWorkload(
            agent_id=agent.id,
            agent_name=agent.name,
            total_assigned_tickets=sum(ticket.assigned_agent_id == agent.id for ticket in tickets),
            open_assigned_tickets=sum(
                ticket.assigned_agent_id == agent.id and ticket.status == "Open" for ticket in tickets
            ),
            in_progress_assigned_tickets=sum(
                ticket.assigned_agent_id == agent.id and ticket.status == "In Progress" for ticket in tickets
            ),
            resolved_assigned_tickets=sum(
                ticket.assigned_agent_id == agent.id and ticket.status == "Resolved" for ticket in tickets
            ),
            critical_assigned_tickets=sum(
                ticket.assigned_agent_id == agent.id and ticket.priority == "Critical" for ticket in tickets
            ),
        )
        for agent in agents
    ]
    categories = Counter(_category(ticket) for ticket in tickets)

    return schemas.DashboardStats(
        total_customers=db.scalar(customer_count_query) or 0,
        total_tickets=len(tickets),
        open_tickets=sum(ticket.status == "Open" for ticket in tickets),
        in_progress_tickets=sum(ticket.status == "In Progress" for ticket in tickets),
        resolved_tickets=sum(ticket.status == "Resolved" for ticket in tickets),
        closed_tickets=sum(ticket.status == "Closed" for ticket in tickets),
        resolved_today=sum(
            ticket.resolved_at is not None and ticket.resolved_at.date() == today
            for ticket in tickets
        ),
        critical_tickets=sum(ticket.priority == "Critical" for ticket in tickets),
        high_priority_tickets=sum(ticket.priority == "High" for ticket in tickets),
        tickets_by_status=_count_values([ticket.status for ticket in tickets], TICKET_STATUSES),
        tickets_by_priority=_count_values([ticket.priority for ticket in tickets], TICKET_PRIORITIES),
        tickets_by_category=dict(sorted(categories.items())),
        recent_tickets=[
            schemas.DashboardRecentTicket(
                id=ticket.id,
                title=ticket.title,
                status=ticket.status,
                priority=ticket.priority,
                category=_category(ticket),
                customer_name=ticket.customer.full_name,
                assigned_agent_name=ticket.assigned_agent.name if ticket.assigned_agent else None,
                created_at=ticket.created_at,
            )
            for ticket in tickets[:5]
        ],
        agent_workloads=workloads,
    )
