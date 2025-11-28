# Auto Test Service
# Runs Python unit tests and returns results

import subprocess
import os

class AutoTestService:
    def __init__(self, base_path):
        self.base_path = base_path

    def run_pytest(self, rel_path=None):
        cwd = self.base_path
        args = ['pytest', '--maxfail=3', '--disable-warnings', '-q']
        if rel_path:
            args.append(rel_path)
        try:
            result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
            return {
                'status': 'ok' if result.returncode == 0 else 'fail',
                'output': result.stdout + '\n' + result.stderr
            }
        except Exception as e:
            return {'status': 'error', 'output': str(e)}

# Singleton instance
auto_test_service = AutoTestService(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
