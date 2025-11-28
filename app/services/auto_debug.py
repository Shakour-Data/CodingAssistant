# Auto Debug Service
# Provides code linting and error suggestion for Python files

import subprocess
import os

class AutoDebugService:
    def __init__(self, base_path):
        self.base_path = base_path

    def lint_python_file(self, rel_path):
        abs_path = os.path.join(self.base_path, rel_path)
        if not os.path.exists(abs_path):
            return {'error': 'File not found'}
        try:
            result = subprocess.run([
                'python', '-m', 'py_compile', abs_path
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return {'status': 'ok', 'message': 'No syntax errors found.'}
            else:
                return {'status': 'error', 'message': result.stderr}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# Singleton instance
auto_debug_service = AutoDebugService(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
