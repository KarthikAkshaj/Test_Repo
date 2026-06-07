"""Business logic for user operations."""

from typing import Optional

from ..models.user import User
from ..utils.auth import hash_password
from ..utils.db import db, safe_commit


def get_user_by_email(email: str) -> Optional[User]:
    """Return a User by email address, or None."""
    return User.query.filter_by(email=email.strip().lower()).first()


def deactivate_user(user_id: int) -> Optional[str]:
    """
    Soft-delete a user account by marking it inactive.
    Returns an error string on failure, None on success.
    """
    user = User.query.get(user_id)
    if user is None:
        return f'User {user_id} not found'
    user.is_active = False
    return safe_commit()


def change_password(user_id: int, new_password: str) -> Optional[str]:
    """
    Update a user's password hash.
    Returns an error string on failure, None on success.
    """
    user = User.query.get(user_id)
    if user is None:
        return f'User {user_id} not found'
    user.password_hash = hash_password(new_password)
    return safe_commit()
