"""Input validation helpers. All functions return an error string or None."""

import re
from typing import Optional


_EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

PASSWORD_MIN_LENGTH = 8
TASK_TITLE_MAX_LENGTH = 200
TASK_DESCRIPTION_MAX_LENGTH = 5000


def validate_email(email: str) -> Optional[str]:
    """Return an error message if the email is invalid, None if valid."""
    if not email or not isinstance(email, str):
        return 'Email is required'
    if not _EMAIL_REGEX.match(email.strip()):
        return 'Invalid email format'
    return None


def validate_password(password: str) -> Optional[str]:
    """Return an error message if the password fails strength requirements."""
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        return f'Password must be at least {PASSWORD_MIN_LENGTH} characters'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one digit'
    return None


def validate_task_title(title: str) -> Optional[str]:
    """Return an error message if the task title is invalid."""
    if not title or not title.strip():
        return 'Task title is required'
    if len(title) > TASK_TITLE_MAX_LENGTH:
        return f'Task title must not exceed {TASK_TITLE_MAX_LENGTH} characters'
    return None


def validate_priority(priority: str) -> Optional[str]:
    """Return an error message if the priority value is not one of the allowed values."""
    valid = {'low', 'medium', 'high', 'critical'}
    if priority not in valid:
        return f"Priority must be one of: {', '.join(sorted(valid))}"
    return None


def validate_status(status: str) -> Optional[str]:
    """Return an error message if the status value is not one of the allowed values."""
    valid = {'todo', 'in_progress', 'review', 'done'}
    if status not in valid:
        return f"Status must be one of: {', '.join(sorted(valid))}"
    return None
