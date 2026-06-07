import pytest

from app.models.task import Task
from app.models.project import Project


@pytest.fixture
def project(db, test_user):
    proj = Project(name='Test Project', owner_id=test_user.id)
    db.session.add(proj)
    db.session.commit()
    return proj


@pytest.fixture
def task(db, project):
    t = Task(title='Sample Task', project_id=project.id, status='todo', priority='medium')
    db.session.add(t)
    db.session.commit()
    return t


def test_list_tasks_requires_auth(client):
    resp = client.get('/api/v1/tasks')
    assert resp.status_code == 401


def test_list_tasks(client, auth_headers, task):
    resp = client.get('/api/v1/tasks', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'items' in data
    assert 'pagination' in data


def test_create_task_success(client, auth_headers, project):
    resp = client.post('/api/v1/tasks', headers=auth_headers, json={
        'title': 'New Task',
        'project_id': project.id,
        'priority': 'high',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['title'] == 'New Task'
    assert data['status'] == 'todo'
    assert data['priority'] == 'high'


def test_create_task_missing_title(client, auth_headers, project):
    resp = client.post('/api/v1/tasks', headers=auth_headers, json={
        'project_id': project.id,
    })
    assert resp.status_code == 400


def test_create_task_invalid_priority(client, auth_headers, project):
    resp = client.post('/api/v1/tasks', headers=auth_headers, json={
        'title': 'Task',
        'project_id': project.id,
        'priority': 'urgent',
    })
    assert resp.status_code == 400


def test_create_task_invalid_due_date(client, auth_headers, project):
    resp = client.post('/api/v1/tasks', headers=auth_headers, json={
        'title': 'Task',
        'project_id': project.id,
        'due_date': 'not-a-date',
    })
    assert resp.status_code == 400


def test_update_task_status(client, auth_headers, task):
    resp = client.patch(f'/api/v1/tasks/{task.id}', headers=auth_headers, json={
        'status': 'in_progress',
    })
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'in_progress'


def test_update_task_invalid_status(client, auth_headers, task):
    resp = client.patch(f'/api/v1/tasks/{task.id}', headers=auth_headers, json={
        'status': 'completed',
    })
    assert resp.status_code == 400


def test_delete_task(client, auth_headers, task):
    resp = client.delete(f'/api/v1/tasks/{task.id}', headers=auth_headers)
    assert resp.status_code == 204


def test_delete_nonexistent_task(client, auth_headers):
    resp = client.delete('/api/v1/tasks/99999', headers=auth_headers)
    assert resp.status_code == 404
