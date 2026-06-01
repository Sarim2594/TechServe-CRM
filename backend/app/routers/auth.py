from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import create_access_token, verify_password
from ..database import get_db
from ..dependencies import get_current_user, require_agent_or_manager
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    return schemas.TokenResponse(access_token=create_access_token(user.email), user=user)


@router.get("/me", response_model=schemas.UserSummary)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout")
def logout(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Logged out successfully"}


@router.get("/users", response_model=list[schemas.UserSummary])
def list_users(
    current_user: User = Depends(require_agent_or_manager), db: Session = Depends(get_db)
) -> list[User]:
    if current_user.role == "manager":
        return list(db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.name)).all())
    return [current_user]
