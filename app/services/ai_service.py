import requests
import json
import os
import time
from app.utils.config import Config
from app.services.model_service import ModelService

class AIService:
    def __init__(self):
        self.models = Config.MODELS
        self.model_service = ModelService()
        self.local_models = {}  # Cache for loaded local models

    def generate_text(self, model_id, prompt, max_tokens=1000, temperature=0.7):
        """Generate text using a model with multiple fallback strategies"""
        try:
            # Check if model exists in configuration
            if model_id not in self.models and not self._is_ollama_available():
                return f"I apologize, but I'm unable to generate text with the requested model at this time. Error: Model {model_id} not found in configuration. Please ensure your AI models are properly configured and running."

            # First try Ollama if available
            if self._is_ollama_available():
                try:
                    return self._generate_with_ollama(model_id, prompt, max_tokens, temperature)
                except Exception as e:
                    print(f"Ollama failed: {e}, trying local models...")

            # Try local model server
            try:
                return self._generate_with_local_server(model_id, prompt, max_tokens, temperature)
            except Exception as e:
                print(f"Local server failed: {e}, trying direct model loading...")

            # Try direct model loading as last resort
            return self._generate_with_direct_model(model_id, prompt, max_tokens, temperature)

        except Exception as e:
            # Final fallback - return a helpful message
            return f"I apologize, but I'm unable to generate text with the requested model at this time. Error: {str(e)}. Please ensure your AI models are properly configured and running."

    def _is_ollama_available(self):
        """Check if Ollama is running"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False

    def _generate_with_ollama(self, model_id, prompt, max_tokens=1000, temperature=0.7):
        """Generate text using Ollama API"""
        model_name = self._get_ollama_model_name()

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            },
            timeout=120
        )

        if response.status_code == 200:
            try:
                result = response.json()
                return result.get('response', '')
            except Exception:
                return 'Error generating text'
        else:
            return 'Error generating text'

    def _generate_with_local_server(self, model_id, prompt, max_tokens=1000, temperature=0.7):
        """Generate text using local model server"""
        config = self.models[model_id]
        port = config['port']

        # Check if model is running
        models = self.model_service.get_models()
        model_info = next((m for m in models if m['id'] == model_id), None)

        if not model_info or not model_info['is_running']:
            # Try to start the model
            start_result = self.model_service.start_model(model_id)
            if not start_result.get('success', False):
                raise Exception(f"Model {model_id} is not available and could not be started")

            # Wait for model to start
            time.sleep(3)

        response = requests.post(
            f'http://localhost:{port}/generate',
            json={
                'prompt': prompt,
                'max_tokens': max_tokens,
                'temperature': temperature
            },
            timeout=60
        )

        if response.status_code == 200:
            try:
                result = response.json()
                return result.get('text', '')
            except Exception:
                raise Exception('Local server error: JSON parsing failed')
        else:
            raise Exception(f'Local server error: {response.status_code}')

    def _generate_with_direct_model(self, model_id, prompt, max_tokens=1000, temperature=0.7):
        """Generate text by directly loading and using a model"""
        try:
            # Import here to avoid issues if libraries aren't available
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch

            # Check if model is cached
            if model_id in self.local_models:
                tokenizer, generator = self.local_models[model_id]
            else:
                # Load model
                config = self.models.get(model_id)
                if not config:
                    raise Exception(f"Model {model_id} not found in configuration")

                model_path = os.path.join(Config.MODELS_DIR, f"{model_id}.bin")
                if not os.path.exists(model_path):
                    raise Exception(f"Model file not found: {model_path}")

                print(f"Loading model {model_id} from {model_path}...")

                tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    local_files_only=True
                )

                generator = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if torch.cuda.is_available() else -1
                )

                # Cache the model
                self.local_models[model_id] = (tokenizer, generator)

            # Generate text
            result = generator(
                prompt,
                max_length=len(tokenizer.encode(prompt)) + max_tokens,
                temperature=temperature,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id
            )

            generated_text = result[0]['generated_text']

            # Remove prompt from result
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()

            return generated_text

        except ImportError as e:
            raise Exception(f"Required libraries not available: {e}")
        except Exception as e:
            raise Exception(f"Direct model loading failed: {e}")

    def _get_ollama_model_name(self):
        """Get the name of the available Ollama model"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                if models:
                    # Prefer coding models if available
                    for model in models:
                        name = model['name'].lower()
                        if 'code' in name or 'llama' in name or 'codellama' in name:
                            return model['name']
                    return models[0]['name']
            return 'llama2'
        except:
            return 'llama2'

    def get_available_models(self):
        """Get list of available models"""
        available = []

        # Check Ollama models
        if self._is_ollama_available():
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get('models', []):
                        available.append({
                            'id': f"ollama-{model['name']}",
                            'name': f"Ollama: {model['name']}",
                            'type': 'ollama'
                        })
            except:
                pass

        # Check local models
        models = self.model_service.get_models()
        for model in models:
            if model['is_downloaded']:
                available.append({
                    'id': model['id'],
                    'name': model['name'],
                    'type': 'local',
                    'running': model['is_running']
                })

        return available
