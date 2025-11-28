# Project Management Service
# Handles tasks, documentation, and file management

import os
import json

class ProjectManagerService:
    def __init__(self, base_path):
        self.base_path = base_path
        self.tasks_file = os.path.join(base_path, 'project_tasks.json')
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump({'tasks': []}, f)

    def get_tasks(self):
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('tasks', [])

    def add_task(self, title, description=None, status='todo'):
        tasks = self.get_tasks()
        task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description or '',
            'status': status
        }
        tasks.append(task)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump({'tasks': tasks}, f, ensure_ascii=False, indent=2)
        return task

    def update_task(self, task_id, **kwargs):
        tasks = self.get_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task.update(kwargs)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump({'tasks': tasks}, f, ensure_ascii=False, indent=2)
        return True

    def delete_task(self, task_id):
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t['id'] != task_id]
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump({'tasks': tasks}, f, ensure_ascii=False, indent=2)
        return True

# Singleton instance
project_manager_service = ProjectManagerService(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
