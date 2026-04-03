from fastapi import HTTPException, status
from app.models.user import User, UserRole


def can_modify_transaction(current_user: User, transaction_owner_id: int):
    """Analysts can only modify their own transactions. Admins can modify any."""
    if current_user.role == UserRole.analyst and current_user.id != transaction_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analysts can only modify their own transactions",
        )


def can_delete_transaction(current_user: User):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete transactions",
        )
