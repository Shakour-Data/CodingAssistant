from flask import Blueprint, render_template, request, jsonify, current_app
import platform
import psutil
import os

from app.services.model_service import ModelService
from app.services.download_service import DownloadService
from app.services.ai_service import AIService
from .services.auto_coding import auto_coding_service
from .services.project_manager import project_manager_service
from .services.auto_debug import auto_debug_service
from .services.auto_planning import auto_planning_service
from .services.auto_test import auto_test_service
from app.models import Project
from app import db
import subprocess
import os

bp = Blueprint('main', __name__)

# Initialize services
model_service = ModelService()
download_service = DownloadService()
ai_service = AIService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/chat')
def chat():
    return render_template('chat.html')

@bp.route('/model-manager')
def model_manager():
    return render_template('model_manager.html')

@bp.route('/settings')
def settings():
    return render_template('settings.html')

@bp.route('/projects')
def projects():
    return render_template('projects.html')

@bp.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models"""
    try:
        models = model_service.get_models()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/models/download', methods=['POST'])
def download_model():
    """Download a model"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')

        if not model_id:
            return jsonify({'error': 'Model ID is required'}), 400

        # Start download in background
        download_service.start_download(model_id)

        return jsonify({'message': 'Download started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/models/start', methods=['POST'])
def start_model():
    """Start a model server"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')

        if not model_id:
            return jsonify({'error': 'Model ID is required'}), 400

        result = model_service.start_model(model_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/models/stop', methods=['POST'])
def stop_model():
    """Stop a model server"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')

        if not model_id:
            return jsonify({'error': 'Model ID is required'}), 400

        result = model_service.stop_model(model_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/models/generate', methods=['POST'])
def generate_text():
    """Generate text using a model"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')
        prompt = data.get('prompt')

        if not model_id or not prompt:
            return jsonify({'error': 'Model ID and prompt are required'}), 400

        result = ai_service.generate_text(model_id, prompt)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/download/status/<model_id>', methods=['GET'])
def download_status(model_id):
    """Get download status for a model"""
    try:
        status = download_service.get_download_status(model_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat with the code assistant model"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')
        prompt = data.get('prompt')
        if not model_id or not prompt:
            return jsonify({'error': 'Model ID and prompt are required'}), 400

        # Check if model is running
        models = model_service.get_models()
        model_info = next((m for m in models if m['id'] == model_id), None)
        if not model_info or not model_info.get('is_running', False):
            return jsonify({'error': f'Model {model_id} is not running. Please start the model first.'}), 400

        result = ai_service.generate_text(model_id, prompt)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/auto-coding', methods=['POST'])
def api_auto_coding():
    """Generate code using AI model"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')
        prompt = data.get('prompt')
        language = data.get('language')
        if not model_id or not prompt:
            return jsonify({'error': 'Model ID and prompt are required'}), 400
        code = auto_coding_service.generate_code(model_id, prompt, language)
        return jsonify({'result': code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Auto Debug API
@bp.route('/api/auto-debug', methods=['POST'])
def api_auto_debug():
    try:
        data = request.get_json()
        rel_path = data.get('file')
        if not rel_path:
            return jsonify({'error': 'File path is required'}), 400
        result = auto_debug_service.lint_python_file(rel_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Project Management APIs
@bp.route('/api/project/tasks', methods=['GET'])
def get_project_tasks():
    try:
        tasks = project_manager_service.get_tasks()
        return jsonify({'tasks': tasks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/project/tasks', methods=['POST'])
def add_project_task():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        task = project_manager_service.add_task(title, description)
        return jsonify({'task': task})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/project/tasks/<int:task_id>', methods=['PUT'])
def update_project_task(task_id):
    try:
        data = request.get_json()
        project_manager_service.update_task(task_id, **data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/project/tasks/<int:task_id>', methods=['DELETE'])
def delete_project_task(task_id):
    try:
        project_manager_service.delete_task(task_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Auto Planning API
@bp.route('/api/auto-planning', methods=['POST'])
def api_auto_planning():
    try:
        data = request.get_json()
        desc = data.get('description')
        result = auto_planning_service.suggest_plan(desc)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Auto Test API
@bp.route('/api/auto-test', methods=['POST'])
def api_auto_test():
    try:
        data = request.get_json()
        rel_path = data.get('file')
        result = auto_test_service.run_pytest(rel_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Auto Develop API: handles full automation from project description
@bp.route('/api/auto-develop', methods=['POST'])
def api_auto_develop():
    try:
        data = request.get_json()
        desc = data.get('description')
        progress = []
        if not desc:
            return jsonify({'error': 'Project description required.'}), 400

        # 1. Analyze project and plan (try AI planning, fallback to basic)
        try:
            plan_result = auto_planning_service.suggest_plan(desc)
            if 'plan' in plan_result:
                progress.append('برنامه‌ریزی پروژه انجام شد.')
                for step in plan_result['plan']:
                    progress.append(f"{step['step']}. {step['title']} - {step['desc']}")
            else:
                progress.append('برنامه‌ریزی پایه انجام شد.')
        except Exception as e:
            # Fallback to basic planning if AI service is not available
            progress.append('برنامه‌ریزی پایه انجام شد (سرویس هوش مصنوعی در دسترس نیست).')

        # 2. Detect project type and create project structure
        project_type = detect_project_type(desc)
        project_name = generate_project_name(desc)
        project_path = create_project_structure(project_name, project_type, progress)

        # 3. Install dependencies
        install_project_dependencies(project_path, project_type, progress)

        # 4. Create basic files and setup
        setup_project_files(project_path, project_type, desc, progress)

        # 5. Save project to database
        project = Project(
            name=project_name,
            description=desc,
            path=project_path,
            status='completed'
        )
        db.session.add(project)
        db.session.commit()

        progress.append(f'پروژه "{project_name}" با موفقیت ایجاد شد.')
        progress.append(f'مسیر پروژه: {project_path}')
        progress.append('شما می‌توانید پروژه را اجرا کنید.')

        return jsonify({
            'progress': progress,
            'project': project.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Projects APIs
@bp.route('/api/projects', methods=['GET'])
def get_projects():
    """Get list of all projects"""
    try:
        projects = Project.query.all()
        return jsonify({'projects': [p.to_dict() for p in projects]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/projects', methods=['POST'])
def add_project():
    """Add a new project"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        path = data.get('path')

        if not name or not path:
            return jsonify({'error': 'Name and path are required'}), 400

        # Check if path exists
        if not os.path.exists(path):
            return jsonify({'error': 'Project path does not exist'}), 400

        project = Project(
            name=name,
            description=description,
            path=path
        )
        db.session.add(project)
        db.session.commit()

        return jsonify({'project': project.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/projects/<int:project_id>/open', methods=['POST'])
def open_project_folder(project_id):
    """Open project folder in file explorer"""
    try:
        project = Project.query.get_or_404(project_id)

        if not os.path.exists(project.path):
            return jsonify({'error': 'Project path no longer exists'}), 404

        # Open folder in file explorer
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', project.path])
        elif os.name == 'posix':  # macOS/Linux
            if 'darwin' in os.uname().sysname.lower():  # macOS
                subprocess.run(['open', project.path])
            else:  # Linux
                subprocess.run(['xdg-open', project.path])

        return jsonify({'success': True, 'message': 'Project folder opened'})
    except Exception as e:
        # Check if it's a NotFound exception
        if hasattr(e, 'code') and e.code == 404:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify({'error': str(e)}), 500

# Helper functions for auto-develop
def detect_project_type(description):
    """Detect project type from description"""
    desc_lower = description.lower()
    if 'web' in desc_lower or 'website' in desc_lower or 'flask' in desc_lower or 'django' in desc_lower:
        return 'web'
    elif 'api' in desc_lower or 'rest' in desc_lower:
        return 'api'
    elif 'data' in desc_lower or 'analysis' in desc_lower or 'pandas' in desc_lower:
        return 'data'
    elif 'machine learning' in desc_lower or 'ml' in desc_lower or 'ai' in desc_lower:
        return 'ml'
    else:
        return 'general'

def generate_project_name(description):
    """Generate project name from description"""
    # Simple name generation - take first few words
    words = description.split()[:3]
    name = '_'.join(words).lower()
    # Remove special characters
    import re
    name = re.sub(r'[^\w]', '', name)
    return name or 'auto_project'

def create_project_structure(project_name, project_type, progress):
    """Create project directory structure"""
    base_dir = os.path.join(os.getcwd(), 'generated_projects')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    project_path = os.path.join(base_dir, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    progress.append(f'ساختار پروژه ایجاد شد: {project_path}')

    # Create basic directories based on project type
    if project_type == 'web':
        dirs = ['templates', 'static/css', 'static/js', 'static/img']
    elif project_type == 'api':
        dirs = ['api', 'models', 'tests']
    elif project_type == 'data':
        dirs = ['data', 'notebooks', 'scripts', 'tests']
    elif project_type == 'ml':
        dirs = ['models', 'data', 'notebooks', 'src', 'tests']
    else:
        dirs = ['src', 'tests']

    for dir_name in dirs:
        dir_path = os.path.join(project_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)

    progress.append('پوشه‌های پروژه ایجاد شدند.')
    return project_path

def install_project_dependencies(project_path, project_type, progress):
    """Install project dependencies"""
    requirements = []

    if project_type == 'web':
        requirements = ['flask', 'flask-sqlalchemy', 'flask-migrate']
    elif project_type == 'api':
        requirements = ['flask', 'flask-restful', 'marshmallow']
    elif project_type == 'data':
        requirements = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter']
    elif project_type == 'ml':
        requirements = ['scikit-learn', 'pandas', 'numpy', 'matplotlib', 'tensorflow', 'jupyter']
    else:
        requirements = ['requests', 'python-dotenv']

    if requirements:
        # Create requirements.txt
        req_file = os.path.join(project_path, 'requirements.txt')
        with open(req_file, 'w') as f:
            f.write('\n'.join(requirements))

        progress.append(f'فایل requirements.txt ایجاد شد با وابستگی‌های: {", ".join(requirements)}')

        # Try to install dependencies
        try:
            subprocess.run(['pip', 'install'] + requirements, cwd=project_path, check=True)
            progress.append('وابستگی‌های پروژه نصب شدند.')
        except subprocess.CalledProcessError:
            progress.append('هشدار: نصب وابستگی‌ها با خطا مواجه شد. لطفاً دستی نصب کنید.')
    else:
        progress.append('پروژه نیاز به وابستگی خاصی ندارد.')

def setup_project_files(project_path, project_type, description, progress):
    """Create basic project files"""
    if project_type == 'web':
        # Create app.py
        app_content = '''from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
'''
        with open(os.path.join(project_path, 'app.py'), 'w') as f:
            f.write(app_content)

        # Create basic template
        template_content = '''<!DOCTYPE html>
<html>
<head>
    <title>My Web App</title>
</head>
<body>
    <h1>Welcome to My Web Application</h1>
    <p>{{description}}</p>
</body>
</html>'''
        with open(os.path.join(project_path, 'templates', 'index.html'), 'w') as f:
            f.write(template_content)

    elif project_type == 'api':
        # Create api.py
        api_content = '''from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
'''
        with open(os.path.join(project_path, 'api.py'), 'w') as f:
            f.write(api_content)

    else:
        # Create main.py for general projects
        main_content = '''#!/usr/bin/env python3
"""
Auto-generated project main file
"""

def main():
    print("Hello from auto-generated project!")
    print("Description: {{description}}")

if __name__ == '__main__':
    main()
'''
        with open(os.path.join(project_path, 'main.py'), 'w') as f:
            f.write(main_content)

    # Create README.md
    readme_content = f'''# {os.path.basename(project_path)}

{description}

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the project:
```bash
python main.py
```

## Project Structure

- `src/`: Source code
- `tests/`: Test files
- `requirements.txt`: Python dependencies
'''
    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write(readme_content)

    progress.append('فایل‌های پایه پروژه ایجاد شدند.')
    progress.append('README.md و فایل‌های اجرایی آماده هستند.')
