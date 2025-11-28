import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MODELS_DIR = os.environ.get('MODELS_DIR') or os.path.join(os.path.dirname(__file__), 'app', 'models')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Model configurations
    MODELS = {
        'gpt4all-j': {
            'name': 'GPT4All-J',
            'url': 'https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin',
            'size': '3.8GB',
            'type': 'ggml',
            'port': 8000
        },
        'llama-2-7b': {
            'name': 'Llama 2 7B',
            'url': 'https://huggingface.co/TheBloke/Llama-2-7B-GGML/resolve/main/llama-2-7b.ggmlv3.q4_0.bin',
            'size': '6.7GB',
            'type': 'ggml',
            'port': 8001
        },
        'mistral-7b': {
            'name': 'Mistral 7B',
            'url': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_0.gguf',
            'size': '4.1GB',
            'type': 'gguf',
            'port': 8002
        },
        'codellama-7b': {
            'name': 'Code Llama 7B',
            'url': 'https://huggingface.co/TheBloke/CodeLlama-7B-GGUF/resolve/main/codellama-7b.Q4_0.gguf',
            'size': '3.8GB',
            'type': 'gguf',
            'port': 8003
        },
        'phi-2': {
            'name': 'Phi-2',
            'url': 'https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_0.gguf',
            'size': '1.7GB',
            'type': 'gguf',
            'port': 8004
        }
    }
