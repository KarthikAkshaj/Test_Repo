"""Project CRUD routes."""

from flask import Blueprint, request, jsonify, current_app

from ..models.project import Project
from ..utils.auth import require_auth
from ..utils.db import db, get_or_404, safe_commit

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
@require_auth
def list_projects():
    """Return all projects accessible to the authenticated user."""
    projects = Project.query.filter_by(owner_id=request.user_id).all()
    return jsonify({'items': [p.to_dict() for p in projects]}), 200


@projects_bp.route('', methods=['POST'])
@require_auth
def create_project():
    """Create a new project owned by the authenticated user."""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    if len(name) > 200:
        return jsonify({'error': 'Project name must not exceed 200 characters'}), 400

    project = Project(
        name=name,
        description=data.get('description'),
        owner_id=request.user_id,
    )
    db.session.add(project)
    err = safe_commit()
    if err:
        current_app.logger.error('Create project failed: %s', err)
        return jsonify({'error': 'Could not create project'}), 500

    return jsonify(project.to_dict()), 201


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id: int):
    """Delete a project and all its tasks (cascade)."""
    project = get_or_404(Project, project_id)
    if project.owner_id != request.user_id:
        return jsonify({'error': 'You do not own this project'}), 403

    db.session.delete(project)
    err = safe_commit()
    if err:
        current_app.logger.error('Delete project %d failed: %s', project_id, err)
        return jsonify({'error': 'Could not delete project'}), 500
    return '', 204
