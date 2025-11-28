from app import db
from datetime import datetime

class Model(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    size = db.Column(db.String(20))
    is_downloaded = db.Column(db.Boolean, default=False)
    is_running = db.Column(db.Boolean, default=False)
    download_progress = db.Column(db.Float, default=0.0)
    port = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'size': self.size,
            'is_downloaded': self.is_downloaded,
            'is_running': self.is_running,
            'download_progress': self.download_progress,
            'port': self.port,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='completed')  # completed, in_progress, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'path': self.path,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
