import os
import requests
import threading
from tqdm import tqdm
from app.utils.config import Config
from app import db
from app.models import Model

class DownloadService:
    def __init__(self):
        self.downloads = {}
        self.lock = threading.Lock()
        self.models_dir = Config.MODELS_DIR
        
    def start_download(self, model_id):
        """Start downloading a model in background"""
        with self.lock:
            if model_id in self.downloads:
                return {'success': False, 'message': 'Download already in progress'}
            
            config = Config.MODELS.get(model_id)
            if not config:
                return {'success': False, 'message': 'Model not found'}
            
            # Start download thread
            thread = threading.Thread(
                target=self._download_model,
                args=(model_id, config)
            )
            thread.daemon = True
            thread.start()
            
            self.downloads[model_id] = {
                'thread': thread,
                'progress': 0.0,
                'status': 'downloading'
            }
            
            return {'success': True, 'message': 'Download started'}
    
    def _download_model(self, model_id, config):
        """Download model file"""
        try:
            url = config['url']
            model_file = os.path.join(self.models_dir, f"{model_id}.bin")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_file), exist_ok=True)
            
            # Start download
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_file, 'wb') as f, tqdm(
                desc=f"Downloading {config['name']}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
                        self._update_progress(model_id, (f.tell() / total_size) * 100)
            # Download completed
            self._update_progress(model_id, 100.0)
            self._update_status(model_id, 'completed')
            
            # Update database
            model_db = Model.query.get(model_id)
            if model_db:
                model_db.is_downloaded = True
                model_db.download_progress = 100.0
                db.session.commit()
            
        except Exception as e:
            # Download failed
            self._update_status(model_id, 'failed')
            print(f"Download failed for {model_id}: {str(e)}")
        finally:
            # Clean up
            with self.lock:
                if model_id in self.downloads:
                    del self.downloads[model_id]
    
    def _update_progress(self, model_id, progress):
        """Update download progress"""
        with self.lock:
            if model_id in self.downloads:
                self.downloads[model_id]['progress'] = progress
                
                # Update database
                model_db = Model.query.get(model_id)
                if model_db:
                    model_db.download_progress = progress
                    db.session.commit()
    
    def _update_status(self, model_id, status):
        """Update download status"""
        with self.lock:
            if model_id in self.downloads:
                self.downloads[model_id]['status'] = status
    
    def get_download_status(self, model_id):
        """Get download status for a model"""
        with self.lock:
            if model_id in self.downloads:
                return {
                    'status': self.downloads[model_id]['status'],
                    'progress': self.downloads[model_id]['progress']
                }
            else:
                # Check if model exists in config
                config = Config.MODELS.get(model_id)
                if not config:
                    return {'status': 'not_found', 'progress': 0.0}

                # Try to check download status from server (for testing purposes)
                try:
                    requests.get('http://example.com', timeout=1)
                except Exception as e:
                    return {'status': 'error', 'progress': 0.0, 'message': str(e)}

                # Check if model is downloaded
                model_file = os.path.join(self.models_dir, f"{model_id}.bin")
                if os.path.exists(model_file):
                    return {'status': 'completed', 'progress': 100.0}
                else:
                    return {'status': 'not_downloaded', 'progress': 0.0}
