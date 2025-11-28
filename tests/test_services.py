import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.services.model_service import ModelService
from app.services.download_service import DownloadService
from app.services.ai_service import AIService
from app.services.project_manager import project_manager_service
from app.services.auto_coding import AutoCodingService
from app.services.auto_debug import AutoDebugService
from app.services.auto_planning import AutoPlanningService
from app.services.auto_test import AutoTestService

# Test ModelService
def test_model_service_get_models(app):
    """Test getting models from ModelService."""
    with app.app_context():
        service = ModelService()
        models = service.get_models()
        assert isinstance(models, list)
        # Assuming there are models defined in config

@patch('subprocess.Popen')
@patch('app.services.model_service.ModelService._wait_for_server')
def test_model_service_start_model(mock_wait, mock_popen, app):
    """Test starting a model."""
    with app.app_context():
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_wait.return_value = True

        service = ModelService()

        # Create a mock model file
        model_name = 'gpt4all-j'
        model_file = os.path.join(service.models_dir, f'{model_name}.bin')
        with open(model_file, 'w') as f:
            f.write('mock model')

        result = service.start_model(model_name)
        assert result['success'] == True

def test_model_service_start_model_not_found(app):
    """Test starting a non-existent model."""
    with app.app_context():
        service = ModelService()
        result = service.start_model('non-existent-model')
        assert result['success'] == False
        assert 'not found' in result['message']

@patch('os.path.exists')
def test_model_service_start_model_not_downloaded(mock_exists, app):
    """Test starting a model that hasn't been downloaded."""
    with app.app_context():
        mock_exists.return_value = False  # Simulate model file not existing
        service = ModelService()
        result = service.start_model('gpt4all-j')  # Model exists in config but file doesn't exist
        assert result['success'] == False
        assert 'not downloaded' in result['message']

def test_model_service_stop_model(app):
    """Test stopping a model."""
    with app.app_context():
        service = ModelService()
        # First start a model
        with patch('subprocess.Popen') as mock_popen, \
             patch.object(service, '_wait_for_server', return_value=True):
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            model_name = 'gpt4all-j'
            model_file = os.path.join(service.models_dir, f'{model_name}.bin')
            with open(model_file, 'w') as f:
                f.write('mock model')

            service.start_model(model_name)

            # Now stop it
            result = service.stop_model(model_name)
            assert result['success'] == True

def test_model_service_stop_model_not_running(app):
    """Test stopping a model that's not running."""
    with app.app_context():
        service = ModelService()
        result = service.stop_model('test-model')
        assert result['success'] == False
        assert 'not running' in result['message']

# Test DownloadService
def test_download_service_init(app):
    """Test DownloadService initialization."""
    service = DownloadService()
    assert hasattr(service, 'downloads')

# Test AIService
def test_ai_service_init(app):
    """Test AIService initialization."""
    service = AIService()
    assert hasattr(service, 'model_service')

@patch('requests.post')
def test_ai_service_generate_text(mock_post, app):
    """Test generating text with AIService."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'text': 'Generated text'}
    mock_post.return_value = mock_response

    service = AIService()
    result = service.generate_text('gpt4all-j', 'Test prompt')
    assert result == 'Generated text'

# Test ProjectManager
def test_project_manager_init(app):
    """Test ProjectManager initialization."""
    from app.services.project_manager import ProjectManagerService
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ProjectManagerService(temp_dir)
        assert hasattr(service, 'base_path')

def test_project_manager_add_task(app):
    """Test adding a task."""
    from app.services.project_manager import ProjectManagerService
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ProjectManagerService(temp_dir)
        task = service.add_task('Test Task', 'Description')
        assert task['title'] == 'Test Task'
        assert task['description'] == 'Description'

def test_project_manager_get_tasks(app):
    """Test getting tasks."""
    from app.services.project_manager import ProjectManagerService
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ProjectManagerService(temp_dir)
        service.add_task('Task 1', 'Desc 1')
        service.add_task('Task 2', 'Desc 2')
        tasks = service.get_tasks()
        assert len(tasks) == 2

def test_project_manager_update_task(app):
    """Test updating a task."""
    from app.services.project_manager import ProjectManagerService
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ProjectManagerService(temp_dir)
        task = service.add_task('Original', 'Original desc')
        service.update_task(task['id'], title='Updated', description='Updated desc')
        tasks = service.get_tasks()
        updated_task = next(t for t in tasks if t['id'] == task['id'])
        assert updated_task['title'] == 'Updated'

def test_project_manager_delete_task(app):
    """Test deleting a task."""
    from app.services.project_manager import ProjectManagerService
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ProjectManagerService(temp_dir)
        task = service.add_task('To Delete', 'Will be deleted')
        service.delete_task(task['id'])
        tasks = service.get_tasks()
        assert len(tasks) == 0

# Test AutoCodingService
def test_auto_coding_service_init(app):
    """Test AutoCodingService initialization."""
    service = AutoCodingService()
    assert hasattr(service, 'ai_service')

# Test AutoDebugService
def test_auto_debug_service_init(app):
    """Test AutoDebugService initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = AutoDebugService(temp_dir)
        assert hasattr(service, 'base_path')

# Test AutoPlanningService
def test_auto_planning_service_init(app):
    """Test AutoPlanningService initialization."""
    service = AutoPlanningService()
    assert hasattr(service, 'suggest_plan')

# Test AutoTestService
def test_auto_test_service_init(app):
    """Test AutoTestService initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = AutoTestService(temp_dir)
        assert hasattr(service, 'base_path')
