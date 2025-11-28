import pytest
import json
from unittest.mock import patch, MagicMock

def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    # Assuming the template renders successfully

def test_dashboard_route(client):
    """Test the dashboard route."""
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_chat_route(client):
    """Test the chat route."""
    response = client.get('/chat')
    assert response.status_code == 200

def test_model_manager_route(client):
    """Test the model manager route."""
    response = client.get('/model-manager')
    assert response.status_code == 200

def test_settings_route(client):
    """Test the settings route."""
    response = client.get('/settings')
    assert response.status_code == 200

def test_get_models_api(client):
    """Test the get models API."""
    response = client.get('/api/models')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'models' in data

@patch('app.routes.model_service')
def test_download_model_api(mock_model_service, client):
    """Test the download model API."""
    mock_download_service = MagicMock()
    with patch('app.routes.download_service', mock_download_service):
        response = client.post('/api/models/download',
                              json={'model_id': 'test-model'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

def test_download_model_api_missing_id(client):
    """Test download model API with missing model_id."""
    response = client.post('/api/models/download', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.model_service')
def test_start_model_api(mock_model_service, client):
    """Test the start model API."""
    mock_model_service.start_model.return_value = {'success': True, 'message': 'Model started'}
    response = client.post('/api/models/start',
                          json={'model_id': 'test-model'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_start_model_api_missing_id(client):
    """Test start model API with missing model_id."""
    response = client.post('/api/models/start', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.model_service')
def test_stop_model_api(mock_model_service, client):
    """Test the stop model API."""
    mock_model_service.stop_model.return_value = {'success': True, 'message': 'Model stopped'}
    response = client.post('/api/models/stop',
                          json={'model_id': 'test-model'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_stop_model_api_missing_id(client):
    """Test stop model API with missing model_id."""
    response = client.post('/api/models/stop', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.ai_service')
def test_generate_text_api(mock_ai_service, client):
    """Test the generate text API."""
    mock_ai_service.generate_text.return_value = 'Generated text'
    response = client.post('/api/models/generate',
                          json={'model_id': 'test-model', 'prompt': 'Test prompt'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data

def test_generate_text_api_missing_params(client):
    """Test generate text API with missing parameters."""
    response = client.post('/api/models/generate', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.ai_service')
@patch('app.routes.model_service')
def test_chat_api(mock_model_service, mock_ai_service, client):
    """Test the chat API."""
    # Mock the model service to return a running model
    mock_model_service.get_models.return_value = [{'id': 'test-model', 'is_running': True}]
    mock_ai_service.generate_text.return_value = 'Chat response'
    response = client.post('/api/chat',
                          json={'model_id': 'test-model', 'prompt': 'Hello'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data

def test_chat_api_missing_params(client):
    """Test chat API with missing parameters."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.download_service')
def test_download_status_api(mock_download_service, client):
    """Test the download status API."""
    mock_download_service.get_download_status.return_value = {'progress': 50}
    response = client.get('/api/download/status/test-model')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'progress' in data

# Test auto-coding API
@patch('app.routes.auto_coding_service')
def test_auto_coding_api(mock_auto_coding_service, client):
    """Test the auto-coding API."""
    mock_auto_coding_service.generate_code.return_value = 'def test(): pass'
    response = client.post('/api/auto-coding',
                          json={'model_id': 'test-model', 'prompt': 'Write a test function'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'result' in data

def test_auto_coding_api_missing_params(client):
    """Test auto-coding API with missing parameters."""
    response = client.post('/api/auto-coding', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test project management APIs
@patch('app.routes.project_manager_service')
def test_get_project_tasks_api(mock_project_manager_service, client):
    """Test the get project tasks API."""
    mock_project_manager_service.get_tasks.return_value = [{'id': 1, 'title': 'Test Task'}]
    response = client.get('/api/project/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tasks' in data

@patch('app.routes.project_manager_service')
def test_add_project_task_api(mock_project_manager_service, client):
    """Test the add project task API."""
    mock_project_manager_service.add_task.return_value = {'id': 1, 'title': 'New Task'}
    response = client.post('/api/project/tasks',
                          json={'title': 'New Task', 'description': 'Description'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'task' in data

def test_add_project_task_api_missing_title(client):
    """Test add project task API with missing title."""
    response = client.post('/api/project/tasks', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.routes.project_manager_service')
def test_update_project_task_api(mock_project_manager_service, client):
    """Test the update project task API."""
    response = client.put('/api/project/tasks/1',
                         json={'title': 'Updated Task'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

@patch('app.routes.project_manager_service')
def test_delete_project_task_api(mock_project_manager_service, client):
    """Test the delete project task API."""
    response = client.delete('/api/project/tasks/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

# Test auto-debug API
@patch('app.routes.auto_debug_service')
def test_auto_debug_api(mock_auto_debug_service, client):
    """Test the auto-debug API."""
    mock_auto_debug_service.lint_python_file.return_value = {'issues': []}
    response = client.post('/api/auto-debug',
                          json={'file': 'test.py'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'issues' in data

def test_auto_debug_api_missing_file(client):
    """Test auto-debug API with missing file."""
    response = client.post('/api/auto-debug', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test auto-planning API
@patch('app.routes.auto_planning_service')
def test_auto_planning_api(mock_auto_planning_service, client):
    """Test the auto-planning API."""
    mock_auto_planning_service.suggest_plan.return_value = {'plan': []}
    response = client.post('/api/auto-planning',
                          json={'description': 'Build a web app'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'plan' in data

# Test auto-test API
@patch('app.routes.auto_test_service')
def test_auto_test_api(mock_auto_test_service, client):
    """Test the auto-test API."""
    mock_auto_test_service.run_pytest.return_value = {'passed': 5, 'failed': 0}
    response = client.post('/api/auto-test',
                          json={'file': 'test_file.py'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'passed' in data

# Test auto-develop API
@patch('app.routes.auto_planning_service')
def test_auto_develop_api(mock_auto_planning_service, client):
    """Test the auto-develop API."""
    mock_auto_planning_service.suggest_plan.return_value = {'plan': []}
    response = client.post('/api/auto-develop',
                          json={'description': 'Build a web app'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'progress' in data

def test_auto_develop_api_missing_description(client):
    """Test auto-develop API with missing description."""
    response = client.post('/api/auto-develop', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test projects APIs
def test_get_projects_api(client, app):
    """Test the get projects API."""
    with app.app_context():
        response = client.get('/api/projects')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'projects' in data

@patch('os.path.exists')
def test_add_project_api(mock_exists, client, app):
    """Test the add project API."""
    with app.app_context():
        mock_exists.return_value = True
        response = client.post('/api/projects',
                              json={'name': 'Test Project', 'description': 'Test', 'path': '/tmp/test'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'project' in data

def test_add_project_api_missing_params(client, app):
    """Test add project API with missing parameters."""
    with app.app_context():
        response = client.post('/api/projects', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

def test_add_project_api_invalid_path(client, app):
    """Test add project API with invalid path."""
    with app.app_context():
        response = client.post('/api/projects',
                              json={'name': 'Test', 'path': '/nonexistent/path'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

@patch('os.path.exists')
@patch('subprocess.run')
@patch('app.routes.Project')
def test_open_project_folder_api(mock_project, mock_subprocess, mock_exists, client, app):
    """Test the open project folder API."""
    with app.app_context():
        mock_project_instance = MagicMock()
        mock_project_instance.path = '/tmp/test'
        mock_project.query.get_or_404.return_value = mock_project_instance
        mock_exists.return_value = True
        mock_subprocess.return_value = None
        response = client.post('/api/projects/1/open')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True

@patch('app.routes.Project')
def test_open_project_folder_api_not_found(mock_project, client, app):
    """Test open project folder API with non-existent project."""
    with app.app_context():
        from werkzeug.exceptions import NotFound
        mock_project.query.get_or_404.side_effect = NotFound()
        response = client.post('/api/projects/999/open')
        assert response.status_code == 404
