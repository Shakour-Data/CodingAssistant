// Model management functionality
class ModelManager {
    constructor() {
        this.models = [];
        this.init();
    }

    async init() {
        await this.loadModels();
        this.setupEventListeners();
        this.startStatusPolling();
    }

    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            this.models = data.models;
            this.renderModels();
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }


    renderModels() {
        const container = document.getElementById('models-container');
        if (!this.models.length) {
            container.innerHTML = '<div class="loader"></div>';
            return;
        }
        container.innerHTML = '';
        this.models.forEach(model => {
            const modelCard = this.createModelCard(model);
            container.appendChild(modelCard);
        });
    }

    createModelCard(model) {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.id = `model-${model.id}`;

        const statusClass = this.getStatusClass(model);
        const statusText = this.getStatusText(model);

        let progressBar = '';
        if (model.download_progress > 0 && model.download_progress < 100) {
            progressBar = `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${model.download_progress}%"></div>
                </div>
                <div class="progress-label">${model.download_progress.toFixed(1)}%</div>
            `;
        }

        card.innerHTML = `
            <div class="model-header">
                <h3 class="model-name">${model.name}</h3>
                <span class="model-status ${statusClass}">${statusText}</span>
            </div>
            <p class="model-description">${model.description || 'No description available'}</p>
            <div class="model-info">
                <span>Size: ${model.size}</span>
                <span>Port: ${model.port}</span>
            </div>
            ${progressBar}
            <div class="model-actions">
                ${this.getActionButtons(model)}
            </div>
        `;
        return card;
    }

    getStatusClass(model) {
        if (model.is_running) return 'status-running';
        if (model.is_downloaded) return 'status-downloaded';
        if (model.download_progress > 0 && model.download_progress < 100) return 'status-downloading';
        return 'status-not-downloaded';
    }

    getStatusText(model) {
        if (model.is_running) return 'Running';
        if (model.is_downloaded) return 'Downloaded';
        if (model.download_progress > 0 && model.download_progress < 100) return 'Downloading';
        return 'Not Downloaded';
    }

    getActionButtons(model) {
        if (model.is_running) {
            return `<button class="btn btn-danger" onclick="modelManager.stopModel('${model.id}')">Stop</button>`;
        } else if (model.is_downloaded) {
            return `<button class="btn btn-success" onclick="modelManager.startModel('${model.id}')">Start</button>`;
        } else if (model.download_progress > 0 && model.download_progress < 100) {
            return `<button class="btn btn-secondary" disabled>Downloading...</button>`;
        } else {
            return `<button class="btn btn-primary" onclick="modelManager.downloadModel('${model.id}')">Download</button>`;
        }
    }

    async downloadModel(modelId) {
        try {
            const response = await fetch('/api/models/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_id: modelId }),
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('Download started', 'success');
                this.startDownloadPolling(modelId);
            } else {
                this.showAlert(data.error || 'Download failed', 'danger');
            }
        } catch (error) {
            console.error('Error downloading model:', error);
            this.showAlert('Download failed', 'danger');
        }
    }

    async startModel(modelId) {
        try {
            const response = await fetch('/api/models/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_id: modelId }),
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showAlert(data.message, 'success');
                await this.loadModels();
            } else {
                this.showAlert(data.error || 'Failed to start model', 'danger');
            }
        } catch (error) {
            console.error('Error starting model:', error);
            this.showAlert('Failed to start model', 'danger');
        }
    }

    async stopModel(modelId) {
        try {
            const response = await fetch('/api/models/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_id: modelId }),
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showAlert(data.message, 'success');
                await this.loadModels();
            } else {
                this.showAlert(data.error || 'Failed to stop model', 'danger');
            }
        } catch (error) {
            console.error('Error stopping model:', error);
            this.showAlert('Failed to stop model', 'danger');
        }
    }

    startStatusPolling() {
        setInterval(async () => {
            await this.loadModels();
        }, 5000);
    }

    showAlert(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => { toast.remove(); }, 4000);
    }

    setupEventListeners() {
        // Additional event listeners can be added here
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.modelManager = new ModelManager();
});
