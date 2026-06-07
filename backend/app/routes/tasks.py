"""Task CRUD routes."""

from datetime import datetime

from flask import Blueprint, request, jsonify, current_app

from ..models.task import Task
from ..utils.auth import require_auth
from ..utils.validators import validate_task_title, validate_priority, validate_status
from ..utils.pagination import get_pagination_params, paginate_query
from ..utils.db import db, get_or_404, safe_commit

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@require_auth
def list_tasks():
    """Return a paginated list of tasks with optional filters."""
    page, per_page = get_pagination_params()

    query = Task.query
    if project_id := request.args.get('project_id'):
        query = query.filter_by(project_id=int(project_id))
    if status := request.args.get('status'):
        query = query.filter_by(status=status)
    if assignee_id := request.args.get('assignee_id'):
        query = query.filter_by(assignee_id=int(assignee_id))

    result = paginate_query(query, page, per_page)
    result['items'] = [t.to_dict() for t in result['items']]
    return jsonify(result), 200


@tasks_bp.route('', methods=['POST'])
@require_auth
def create_task():
    """Create a new task."""
    data = request.get_json(silent=True) or {}

    title = data.get('title', '')
    title_err = validate_task_title(title)
    if title_err:
        return jsonify({'error': title_err}), 400

    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    priority = data.get('priority', 'medium')
    priority_err = validate_priority(priority)
    if priority_err:
        return jsonify({'error': priority_err}), 400

    due_date = None
    if raw_due := data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(raw_due)
        except ValueError:
            return jsonify({'error': 'due_date must be an ISO 8601 datetime string'}), 400

    task = Task(
        title=title.strip(),
        description=data.get('description'),
        project_id=project_id,
        assignee_id=data.get('assignee_id'),
        priority=priority,
        due_date=due_date,
        status='todo',
    )
    db.session.add(task)
    err = safe_commit()
    if err:
        current_app.logger.error('Create task commit failed: %s', err)
        return jsonify({'error': 'Could not create task'}), 500

    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<int:task_id>', methods=['PATCH'])
@require_auth
def update_task(task_id: int):
    """Partially update a task."""
    task = get_or_404(Task, task_id)
    data = request.get_json(silent=True) or {}

    if 'title' in data:
        err = validate_task_title(data['title'])
        if err:
            return jsonify({'error': err}), 400
        task.title = data['title'].strip()

    if 'status' in data:
        err = validate_status(data['status'])
        if err:
            return jsonify({'error': err}), 400
        task.status = data['status']

    if 'priority' in data:
        err = validate_priority(data['priority'])
        if err:
            return jsonify({'error': err}), 400
        task.priority = data['priority']

    if 'description' in data:
        task.description = data['description']

    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']

    if 'due_date' in data:
        if data['due_date'] is None:
            task.due_date = None
        else:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'due_date must be an ISO 8601 datetime string'}), 400

    err = safe_commit()
    if err:
        current_app.logger.error('Update task %d failed: %s', task_id, err)
        return jsonify({'error': 'Could not update task'}), 500

    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id: int):
    """Delete a task."""
    task = get_or_404(Task, task_id)
    db.session.delete(task)
    err = safe_commit()
    if err:
        current_app.logger.error('Delete task %d failed: %s', task_id, err)
        return jsonify({'error': 'Could not delete task'}), 500
    return '', 204
