from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies import require_agent_or_manager, require_manager
from ..models import Customer, Ticket, User

router = APIRouter(prefix="/customers", tags=["customers"])


def _accessible_customers(current_user: User):
    query = select(Customer).order_by(Customer.created_at.desc())
    if current_user.role == "agent":
        query = query.where(Customer.assigned_agent_id == current_user.id)
    return query


def _get_customer(customer_id: int, current_user: User, db: Session) -> Customer:
    customer = db.scalar(_accessible_customers(current_user).where(Customer.id == customer_id))
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


def _validate_agent(agent_id: int | None, db: Session) -> None:
    if agent_id is None:
        return
    agent = db.get(User, agent_id)
    if not agent or agent.role != "agent" or not agent.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned agent is invalid")


def _normalize_optional_text(values: dict) -> dict:
    # Empty strings remain compatible with SQLite databases created by the initial scaffold.
    for field in ("phone", "company"):
        if field in values and values[field] is None:
            values[field] = ""
    return values


@router.get("", response_model=list[schemas.CustomerResponse])
def list_customers(
    search: str | None = Query(default=None),
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> list[Customer]:
    query = _accessible_customers(current_user)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Customer.full_name.ilike(pattern),
                Customer.email.ilike(pattern),
                Customer.company.ilike(pattern),
            )
        )
    return list(db.scalars(query).all())


@router.get("/{customer_id}", response_model=schemas.CustomerDetailResponse)
def get_customer(
    customer_id: int,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> dict:
    customer = _get_customer(customer_id, current_user, db)
    ticket_query = select(Ticket).where(Ticket.customer_id == customer.id).order_by(Ticket.created_at.desc())
    if current_user.role == "agent":
        ticket_query = ticket_query.where(Ticket.assigned_agent_id == current_user.id)
    customer_data = schemas.CustomerResponse.model_validate(customer).model_dump()
    customer_data["ticket_history"] = list(db.scalars(ticket_query).all())
    return customer_data


@router.post("", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: schemas.CustomerCreate,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> Customer:
    values = _normalize_optional_text(payload.model_dump())
    if current_user.role == "agent":
        values["assigned_agent_id"] = current_user.id
    _validate_agent(values.get("assigned_agent_id"), db)
    customer = Customer(**values)
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer email already exists")
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int,
    payload: schemas.CustomerUpdate,
    current_user: User = Depends(require_agent_or_manager),
    db: Session = Depends(get_db),
) -> Customer:
    customer = _get_customer(customer_id, current_user, db)
    updates = payload.model_dump(exclude_unset=True)
    if any(field in updates and updates[field] is None for field in ("full_name", "email")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name and email cannot be empty",
        )
    updates = _normalize_optional_text(updates)
    if current_user.role == "agent" and updates.get("assigned_agent_id", current_user.id) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agents cannot reassign customers")
    _validate_agent(updates.get("assigned_agent_id"), db)
    for key, value in updates.items():
        setattr(customer, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer email already exists")
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    _: User = Depends(require_manager),
    db: Session = Depends(get_db),
) -> None:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if db.scalar(select(Ticket.id).where(Ticket.customer_id == customer_id).limit(1)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete the customer's tickets before deleting this customer",
        )
    db.delete(customer)
    db.commit()
