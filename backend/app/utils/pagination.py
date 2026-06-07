"""Pagination helpers for Flask-SQLAlchemy queries."""

from typing import Any, Dict
from flask import request


def get_pagination_params() -> tuple[int, int]:
    """
    Extract page and per_page from query string with safe defaults.
    Returns (page, per_page) where page >= 1 and 1 <= per_page <= 100.
    """
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
    except (ValueError, TypeError):
        page, per_page = 1, 20
    return page, per_page


def paginate_query(query: Any, page: int, per_page: int) -> Dict[str, Any]:
    """
    Apply offset/limit to a SQLAlchemy query and return items with pagination metadata.

    Returns:
        {
            "items": [...],
            "pagination": {"page": int, "per_page": int, "total": int, "pages": int}
        }
    """
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': total_pages,
        },
    }
