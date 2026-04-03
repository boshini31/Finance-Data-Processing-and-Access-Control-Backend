from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(user_id: int, data: UserUpdate, db: Session) -> User:
    user = get_user_by_id(user_id, db)

    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(user_id: int, db: Session) -> dict:
    user = get_user_by_id(user_id, db)
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} has been deactivated"}
