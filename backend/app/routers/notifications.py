from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies import require_agent_or_manager, require_manager
from ..models import NotificationLog, Ticket, User
from ..services.messaging_service import send_ticket_notification

router = APIRouter(tags=["notifications"])


def _get_accessible_ticket(ticket_id: int, current_user: User, db: Session) -> Ticket:
    query = select(Ticket).where(Ticket.id == ticket_id)
    if current_user.role == "agent":
        query = query.where(Ticket.assigned_agent_id == current_user.id)
    ticket = db.scalar(query)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.get("/notifications", response_model=list[schemas.NotificationLogOut])
def list_notifications(
    _: User = Depends(require_manager), db: Session = Depends(get_db)
) -> list[NotificationLog]:
    return list(db.scalars(select(NotificationLog).order_by(NotificationLog.sent_at.desc())).all())


@router.get("/tickets/{ticket_id}/notifications", response_model=list[schemas.NotificationLogOut])
def list_ticket_notifications(
    ticket_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> list[NotificationLog]:
    _get_accessible_ticket(ticket_id, current_user, db)
    return list(
        db.scalars(
            select(NotificationLog)
            .where(NotificationLog.ticket_id == ticket_id)
            .order_by(NotificationLog.sent_at.desc())
        ).all()
    )


@router.post("/tickets/{ticket_id}/notifications/test", response_model=schemas.NotificationLogOut)
async def send_test_notification(
    ticket_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
) -> NotificationLog:
    ticket = _get_accessible_ticket(ticket_id, current_user, db)
    result = await send_ticket_notification(db, ticket, "ticket_test")
    return result.notification
