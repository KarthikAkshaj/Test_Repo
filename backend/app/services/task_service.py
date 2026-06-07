"""Business logic for task operations."""

from typing import List, Optional

from ..models.task import Task
from ..utils.db import db, safe_commit

MAX_BULK_TASK_IDS = 500


def get_tasks_for_project(project_id: int, status: Optional[str] = None) -> List[Task]:
    """Return all tasks for a project, optionally filtered by status."""
    query = Task.query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    return query.all()


def assign_task(task_id: int, assignee_id: Optional[int]) -> Optional[str]:
    """
    Assign (or unassign) a task. Returns an error string on failure, None on success.
    """
    task = Task.query.get(task_id)
    if task is None:
        return f'Task {task_id} not found'
    task.assignee_id = assignee_id
    return safe_commit()


def bulk_update_status(task_ids: List[int], new_status: str) -> dict:
    """
    Update the status field on a batch of tasks.

    Returns {"updated": int, "not_found": List[int]}.
    Raises ValueError if task_ids exceeds MAX_BULK_TASK_IDS or new_status is invalid.
    """
    from ..utils.validators import validate_status
    status_err = validate_status(new_status)
    if status_err:
        raise ValueError(status_err)

    if len(task_ids) > MAX_BULK_TASK_IDS:
        raise ValueError(f'Cannot update more than {MAX_BULK_TASK_IDS} tasks at once')

    found_tasks = Task.query.filter(Task.id.in_(task_ids)).all()
    found_ids = {t.id for t in found_tasks}
    not_found = [tid for tid in task_ids if tid not in found_ids]

    for task in found_tasks:
        task.status = new_status

    safe_commit()
    return {'updated': len(found_tasks), 'not_found': not_found}


def delete_tasks_for_project(project_id: int) -> int:
    """Delete all tasks belonging to a project. Returns the number of deleted rows."""
    count = Task.query.filter_by(project_id=project_id).delete()
    safe_commit()
    return count
