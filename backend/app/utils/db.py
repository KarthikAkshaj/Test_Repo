"""Database access helpers."""

from typing import Optional, Type, TypeVar

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
T = TypeVar('T')


def get_or_404(model: Type[T], record_id: int) -> T:
    """Fetch a record by primary key. Aborts with 404 if not found."""
    record = model.query.get(record_id)
    if record is None:
        from flask import abort
        abort(404, description=f'{model.__name__} with id {record_id} not found')
    return record


def safe_commit() -> Optional[str]:
    """
    Commit the current session.
    Returns None on success, or an error string if the commit fails (and rolls back).
    """
    try:
        db.session.commit()
        return None
    except Exception as exc:
        db.session.rollback()
        return str(exc)
