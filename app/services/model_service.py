import os
import subprocess
import time
import signal
import json
import requests
from threading import Thread, Lock
from app.utils.config import Config
from app import db
from app.models import Model

class ModelService:
    def __init__(self):
        self.running_models = {}
        self.lock = Lock()
        self.models_dir = Config.MODELS_DIR

    def get_models(self):
        """Get list of all models with their status"""
        models = []

        # Always include models from config, regardless of download status
        available_models = dict(Config.MODELS)

        # Scan downloads directory for actual downloaded models
        downloads_dir = os.path.join(self.models_dir, 'downloads')
        downloaded_models = self._scan_downloaded_models(downloads_dir)

        # Merge with downloaded models
        for model_id, config in downloaded_models.items():
            if model_id not in available_models:
                available_models[model_id] = config

        # Include any .bin files in the models directory as available models
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.bin'):
                    model_id = filename[:-4]  # Remove .bin extension
                    if model_id not in available_models:
                        # Create a basic config for this model
                        available_models[model_id] = {
                            'name': model_id.replace('-', ' ').title(),
                            'description': f'Local model: {model_id}',
                            'size': 'Unknown',
                            'type': 'ggml',
                            'port': 8000
                        }

        for model_id, config in available_models.items():
            # Check if model exists in database
            model_db = Model.query.get(model_id)

            if not model_db:
                # Create new model entry
                model_db = Model(
                    id=model_id,
                    name=config['name'],
                    description=config.get('description', ''),
                    size=config.get('size', 'Unknown'),
                    port=config.get('port', 8000)
                )
                db.session.add(model_db)
                db.session.commit()

            # Check if model is downloaded (for Ollama models, check if blobs exist)
            is_downloaded = self._is_model_downloaded(model_id, config)

            # Update database
            if model_db.is_downloaded != is_downloaded:
                model_db.is_downloaded = is_downloaded
                db.session.commit()

            # Check if model is running
            is_running = model_id in self.running_models

            # Update database
            if model_db.is_running != is_running:
                model_db.is_running = is_running
                db.session.commit()

            models.append({
                'id': model_id,
                'name': config['name'],
                'description': config.get('description', ''),
                'size': config.get('size', 'Unknown'),
                'is_downloaded': is_downloaded,
                'is_running': is_running,
                'port': config.get('port', 8000),
                'download_progress': model_db.download_progress
            })

        return models

    def _scan_downloaded_models(self, downloads_dir):
        """Scan downloads directory for Ollama models"""
        available_models = {}

        ollama_dir = os.path.join(downloads_dir, 'Ollama')
        if os.path.exists(ollama_dir):
            # Look for manifest files or model directories
            for item in os.listdir(ollama_dir):
                item_path = os.path.join(ollama_dir, item)
                if os.path.isdir(item_path) and item != 'blobs':
                    # This might be a model directory
                    model_name = item
                    available_models[model_name] = {
                        'name': model_name.replace('-', ' ').title(),
                        'description': f'Ollama model: {model_name}',
                        'size': 'Unknown',
                        'type': 'ollama',
                        'port': 11434  # Default Ollama port
                    }

        # If no specific model directories, check if blobs exist (indicating some models are downloaded)
        blobs_dir = os.path.join(ollama_dir, 'blobs')
        if os.path.exists(blobs_dir) and os.listdir(blobs_dir):
            # Generic Ollama model entry
            available_models['ollama-model'] = {
                'name': 'Ollama Model',
                'description': 'Downloaded Ollama model',
                'size': 'Unknown',
                'type': 'ollama',
                'port': 11434
            }

        return available_models

    def _is_model_downloaded(self, model_id, config):
        """Check if a model is downloaded"""
        if config.get('type') == 'ollama':
            # For Ollama models, check if blobs directory has files
            blobs_dir = os.path.join(self.models_dir, 'downloads', 'Ollama', 'blobs')
            return os.path.exists(blobs_dir) and bool(os.listdir(blobs_dir))
        else:
            # For traditional models, check for .bin file
            model_file = os.path.join(self.models_dir, f"{model_id}.bin")
            return os.path.exists(model_file)

    def start_model(self, model_id):
        """Start a model server"""
        with self.lock:
            if model_id in self.running_models:
                return {'success': False, 'message': 'Model is already running'}

            # Check if it's an Ollama model
            if model_id.startswith('ollama-') or model_id == 'ollama-model':
                return self._start_ollama_model(model_id)

            # Traditional model
            config = Config.MODELS.get(model_id)
            if not config:
                return {'success': False, 'message': 'Model not found'}

            model_file = os.path.join(self.models_dir, f"{model_id}.bin")
            if not os.path.exists(model_file):
                return {'success': False, 'message': 'Model not downloaded'}

            # Start model server
            port = config['port']
            cmd = [
                'python', 'model_server.py',
                '--model', model_file,
                '--port', str(port),
                '--model-type', config['type']
            ]

            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                self.running_models[model_id] = {'process': process, 'port': port}

                # Wait for server to start
                if self._wait_for_server(port):
                    return {'success': True, 'message': 'Model started'}
                else:
                    process.terminate()
                    del self.running_models[model_id]
                    return {'success': False, 'message': 'Failed to start model server'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    def _start_ollama_model(self, model_id):
        """Start an Ollama model (actually just check if Ollama is running)"""
        try:
            # Check if Ollama service is running
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                # Ollama is running, mark model as "running"
                self.running_models[model_id] = {'process': None, 'port': 11434}
                return {'success': True, 'message': 'Ollama model ready'}
            else:
                return {'success': False, 'message': 'Ollama service is not running'}
        except Exception as e:
            return {'success': False, 'message': f'Cannot connect to Ollama: {str(e)}. Make sure Ollama is installed and running.'}

    def stop_model(self, model_id):
        """Stop a model server"""
        with self.lock:
            if model_id not in self.running_models:
                return {'success': False, 'message': 'Model is not running'}

            model_info = self.running_models[model_id]
            process = model_info['process']

            # Handle Ollama models differently
            if model_id.startswith('ollama-') or model_id == 'ollama-model':
                # For Ollama models, just remove from running models
                del self.running_models[model_id]

                # Update database
                model_db = Model.query.get(model_id)
                if model_db:
                    model_db.is_running = False
                    db.session.commit()

                return {'success': True, 'message': 'Ollama model stopped'}

            try:
                process.terminate()
                process.wait(timeout=5)

                del self.running_models[model_id]

                # Update database
                model_db = Model.query.get(model_id)
                if model_db:
                    model_db.is_running = False
                    db.session.commit()

                return {'success': True, 'message': 'Model stopped'}

            except Exception as e:
                return {'success': False, 'message': str(e)}

    def _wait_for_server(self, port, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(f'http://localhost:{port}/health', timeout=1)
                if response.status_code == 200:
                    return True
            except:
                pass

            time.sleep(1)

        return False
