from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies import require_agent_or_manager, require_manager
from ..models import Customer, Ticket, TicketActivity, TicketComment, User
from ..services import ai_service
from ..services.messaging_service import send_ticket_notification

router = APIRouter(prefix="/tickets", tags=["tickets"])

TRACKED_ACTIVITY_ACTIONS = {
    "status": "Status changed",
    "priority": "Priority changed",
    "category": "Category changed",
    "assigned_agent_id": "Assigned agent changed",
}


def _accessible_tickets(current_user: User):
    query = select(Ticket).order_by(Ticket.updated_at.desc())
    if current_user.role == "agent":
        query = query.where(Ticket.assigned_agent_id == current_user.id)
    return query


def _get_ticket(ticket_id: int, current_user: User, db: Session) -> Ticket:
    ticket = db.scalar(_accessible_tickets(current_user).where(Ticket.id == ticket_id))
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def _validate_agent(agent_id: int | None, db: Session) -> None:
    if agent_id is None:
        return
    agent = db.get(User, agent_id)
    if not agent or agent.role != "agent" or not agent.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned agent is invalid")


def _validate_customer(customer_id: int, current_user: User, db: Session) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer is invalid")
    if current_user.role == "agent" and customer.assigned_agent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer is not assigned to you")
    return customer


def _add_activity(
    db: Session,
    ticket_id: int,
    actor_id: int,
    action: str,
    old_value: str | None = None,
    new_value: str | None = None,
) -> None:
    db.add(
        TicketActivity(
            ticket_id=ticket_id,
            actor_id=actor_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
        )
    )


def _get_comments(ticket_id: int, db: Session) -> list[TicketComment]:
    return list(
        db.scalars(
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at)
        ).all()
    )


def _escalation_recommended(ticket: Ticket) -> bool:
    return ticket.ai_sentiment == "Frustrated" and ticket.priority in {"Low", "Medium"}


@router.get("", response_model=list[schemas.TicketOut])
def list_tickets(
    status_filter: schemas.TicketStatus | None = Query(default=None, alias="status"),
    priority: schemas.TicketPriority | None = Query(default=None),
    agent_id: int | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> list[Ticket]:
    query = _accessible_tickets(current_user)
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority:
        query = query.where(Ticket.priority == priority)
    if agent_id:
        query = query.where(Ticket.assigned_agent_id == agent_id)
    if customer_id:
        query = query.where(Ticket.customer_id == customer_id)
    if search:
        pattern = f"%{search}%"
        query = query.join(Customer, Ticket.customer_id == Customer.id).where(
            or_(
                Ticket.title.ilike(pattern),
                Ticket.description.ilike(pattern),
                Ticket.category.ilike(pattern),
                Customer.full_name.ilike(pattern),
            )
        )
    if date_from:
        query = query.where(Ticket.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.where(Ticket.created_at <= datetime.combine(date_to, time.max))
    return list(db.scalars(query).all())


@router.get("/{ticket_id}", response_model=schemas.TicketDetailOut)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> dict:
    ticket = _get_ticket(ticket_id, current_user, db)
    comments = _get_comments(ticket.id, db)
    activity_log = list(
        db.scalars(
            select(TicketActivity)
            .where(TicketActivity.ticket_id == ticket.id)
            .order_by(TicketActivity.created_at.desc())
        ).all()
    )
    ticket_data = schemas.TicketOut.model_validate(ticket).model_dump()
    ticket_data["comments"] = comments
    ticket_data["activity_log"] = activity_log
    return ticket_data


@router.post("", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: schemas.TicketCreate,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> Ticket:
    values = payload.model_dump()
    _validate_customer(values["customer_id"], current_user, db)
    if current_user.role == "agent":
        values["assigned_agent_id"] = current_user.id
    _validate_agent(values.get("assigned_agent_id"), db)
    values["ai_category"] = ai_service.classify_ticket(values["title"], values["description"])
    values["ai_sentiment"] = ai_service.analyze_sentiment(values["title"], values["description"])
    if not values.get("category"):
        values["category"] = values["ai_category"]

    ticket = Ticket(**values)
    db.add(ticket)
    db.flush()
    _add_activity(db, ticket.id, current_user.id, "Ticket created", None, ticket.status)
    db.commit()
    db.refresh(ticket)
    await send_ticket_notification(db, ticket, "ticket_created")
    return ticket


@router.put("/{ticket_id}", response_model=schemas.TicketOut)
async def update_ticket(
    ticket_id: int,
    payload: schemas.TicketUpdate,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = _get_ticket(ticket_id, current_user, db)
    updates = payload.model_dump(exclude_unset=True)
    if "customer_id" in updates:
        _validate_customer(updates["customer_id"], current_user, db)
    if current_user.role == "agent" and updates.get("assigned_agent_id", current_user.id) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agents cannot reassign tickets")
    _validate_agent(updates.get("assigned_agent_id"), db)

    previous_status = ticket.status
    previous_priority = ticket.priority
    for key, value in updates.items():
        old_value = getattr(ticket, key)
        if old_value != value:
            action = TRACKED_ACTIVITY_ACTIONS.get(key, f"{key.replace('_', ' ').title()} changed")
            _add_activity(db, ticket.id, current_user.id, action, str(old_value), str(value))
            setattr(ticket, key, value)

    if "title" in updates or "description" in updates:
        previous_ai_category = ticket.ai_category
        ticket.ai_category = ai_service.classify_ticket(ticket.title, ticket.description)
        ticket.ai_sentiment = ai_service.analyze_sentiment(ticket.title, ticket.description)
        if not ticket.category or ticket.category == previous_ai_category:
            ticket.category = ticket.ai_category
    if ticket.status == "Resolved" and previous_status != "Resolved":
        ticket.resolved_at = datetime.utcnow()
        comments = _get_comments(ticket.id, db)
        ticket.ai_summary = ai_service.summarize_ticket(ticket, comments)
        _add_activity(db, ticket.id, current_user.id, "Ticket resolved", previous_status, ticket.status)
    elif ticket.status == "Closed" and previous_status != "Closed":
        _add_activity(db, ticket.id, current_user.id, "Ticket closed", previous_status, ticket.status)
    elif previous_status == "Resolved" and ticket.status != "Resolved":
        ticket.resolved_at = None

    db.commit()
    db.refresh(ticket)
    if ticket.priority == "Critical" and previous_priority != "Critical":
        await send_ticket_notification(db, ticket, "ticket_critical")
    if ticket.status == "Resolved" and previous_status != "Resolved":
        await send_ticket_notification(db, ticket, "ticket_resolved")
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    _: User = Depends(require_manager),
    db: Session = Depends(get_db),
) -> None:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    db.delete(ticket)
    db.commit()


@router.get("/{ticket_id}/comments", response_model=list[schemas.TicketCommentOut])
def list_comments(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> list[TicketComment]:
    _get_ticket(ticket_id, current_user, db)
    return list(
        db.scalars(
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at)
        ).all()
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=schemas.TicketCommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: int,
    payload: schemas.TicketCommentCreate,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> TicketComment:
    _get_ticket(ticket_id, current_user, db)
    comment = TicketComment(ticket_id=ticket_id, agent_id=current_user.id, **payload.model_dump())
    db.add(comment)
    _add_activity(db, ticket_id, current_user.id, "Comment added", None, payload.message[:180])
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{ticket_id}/activity", response_model=list[schemas.TicketActivityOut])
def list_activity(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> list[TicketActivity]:
    _get_ticket(ticket_id, current_user, db)
    return list(
        db.scalars(
            select(TicketActivity)
            .where(TicketActivity.ticket_id == ticket_id)
            .order_by(TicketActivity.created_at.desc())
        ).all()
    )


@router.get("/{ticket_id}/suggest-response")
def get_suggested_response(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    ticket = _get_ticket(ticket_id, current_user, db)
    return {
        "suggested_response": ai_service.suggest_response(ticket, ticket.customer, _get_comments(ticket.id, db))
    }


@router.post("/{ticket_id}/ai/analyze", response_model=schemas.TicketAIAnalysis)
def analyze_ticket(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> schemas.TicketAIAnalysis:
    ticket = _get_ticket(ticket_id, current_user, db)
    previous_ai_category = ticket.ai_category
    ticket.ai_category = ai_service.classify_ticket(ticket.title, ticket.description)
    ticket.ai_sentiment = ai_service.analyze_sentiment(ticket.title, ticket.description)
    if not ticket.category or ticket.category == previous_ai_category:
        ticket.category = ticket.ai_category
    _add_activity(
        db,
        ticket.id,
        current_user.id,
        "AI analysis refreshed",
        None,
        f"{ticket.ai_category} | {ticket.ai_sentiment}",
    )
    db.commit()
    db.refresh(ticket)
    return schemas.TicketAIAnalysis(
        ai_category=ticket.ai_category,
        ai_sentiment=ticket.ai_sentiment,
        escalation_recommended=_escalation_recommended(ticket),
    )


@router.post("/{ticket_id}/ai/suggest-response", response_model=schemas.TicketAISuggestion)
def suggest_ticket_response(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> schemas.TicketAISuggestion:
    ticket = _get_ticket(ticket_id, current_user, db)
    return schemas.TicketAISuggestion(
        suggestion=ai_service.suggest_response(ticket, ticket.customer, _get_comments(ticket.id, db))
    )


@router.post("/{ticket_id}/ai/summarize", response_model=schemas.TicketAISummary)
def summarize_ticket(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> schemas.TicketAISummary:
    ticket = _get_ticket(ticket_id, current_user, db)
    ticket.ai_summary = ai_service.summarize_ticket(ticket, _get_comments(ticket.id, db))
    _add_activity(db, ticket.id, current_user.id, "AI summary refreshed", None, ticket.ai_summary[:180])
    db.commit()
    db.refresh(ticket)
    return schemas.TicketAISummary(summary=ticket.ai_summary)
