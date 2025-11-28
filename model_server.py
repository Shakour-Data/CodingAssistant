#!/usr/bin/env python3
import argparse
import os
import sys
import json
import time
import signal
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
model = None
tokenizer = None
model_name = None
model_path = None
generator = None

def load_model(model_path_arg, model_name_arg):
    """Load model and tokenizer"""
    global model, tokenizer, model_name, model_path, generator
    
    model_path = model_path_arg
    model_name = model_name_arg
    
    logger.info(f"Loading model from {model_path}")
    
    try:
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            load_in_8bit=True if torch.cuda.is_available() else False
        )
        
        # Create generator
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "model": model_name})

@app.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using the model"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        if not generator:
            return jsonify({"error": "Model not loaded"}), 500
        
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
        
        return jsonify({"text": generated_text})
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Model information"""
    return jsonify({
        "model_name": model_name,
        "model_path": model_path,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    })

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutting down server...")
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Local AI Model Server')
    parser.add_argument('--model', type=str, required=True, help='Path to model file')
    parser.add_argument('--port', type=int, required=True, help='Port number')
    parser.add_argument('--model-type', type=str, default='ggml', help='Model type (ggml, gguf)')
    parser.add_argument('--host', type=str, default='localhost', help='Host address')
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load model
    if not load_model(args.model, os.path.basename(args.model)):
        logger.error("Failed to load model. Exiting...")
        sys.exit(1)
    
    # Start server
    logger.info(f"Starting server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
