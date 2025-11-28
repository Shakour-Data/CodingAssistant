# Auto Coding Service
# Provides code generation and completion using AI models

from .ai_service import AIService
from .model_service import ModelService

class AutoCodingService:
    def __init__(self):
        self.ai_service = AIService()
        self.model_service = ModelService()

    def generate_code(self, model_id, prompt, language=None):
        try:
            # Check if model is available and running
            models = self.model_service.get_models()
            model_info = next((m for m in models if m['id'] == model_id), None)

            if not model_info:
                # Model not found, generate mock code
                return self._generate_mock_code(prompt, language)

            if not model_info['is_downloaded']:
                # Model not downloaded, generate mock code
                return self._generate_mock_code(prompt, language)

            if not model_info['is_running']:
                # Try to start the model
                start_result = self.model_service.start_model(model_id)
                if not start_result.get('success', False):
                    # Failed to start model, generate mock code
                    return self._generate_mock_code(prompt, language)

                # Wait a bit for the model to start
                import time
                time.sleep(2)

            # Optionally, add language-specific prompt engineering
            code_prompt = prompt
            if language:
                code_prompt = f"Write {language} code for: {prompt}"

            return self.ai_service.generate_text(model_id, code_prompt)

        except Exception as e:
            # Handle connection errors or other issues gracefully
            # Generate mock code as fallback
            return self._generate_mock_code(prompt, language)

    def _generate_mock_code(self, prompt, language=None):
        """Generate mock code when AI model is not available"""
        if language and language.lower() == 'python':
            return '''# Mock Python code for: {0}
def mock_function():
    """
    This is a mock implementation.
    Please download and start an AI model for actual code generation.
    """
    print("Mock function executed")
    return "mock_result"

# Example usage
if __name__ == "__main__":
    result = mock_function()
    print("Result: {{}}".format(result))'''.format(prompt)

        elif language and language.lower() == 'javascript':
            return '''// Mock JavaScript code for: {0}
/**
 * This is a mock implementation.
 * Please download and start an AI model for actual code generation.
 */
function mockFunction() {{
    console.log("Mock function executed");
    return "mock_result";
}}

// Example usage
const mockResult = mockFunction();
console.log("Result: " + mockResult);'''.format(prompt)

        elif language and language.lower() == 'html':
            return '''<!-- Mock HTML code for: {0} -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mock Page</title>
</head>
<body>
    <h1>Mock HTML Page</h1>
    <p>This is a mock implementation. Please download and start an AI model for actual code generation.</p>
    <p>Prompt: {0}</p>
</body>
</html>'''.format(prompt)

        else:
            return '''# Mock code for: {0}

# This is a mock implementation.
# Please download and start an AI model for actual code generation.
# The AI model server is not available or not properly configured.

print("Mock code executed")
print("Prompt: {0}")
print("Language: {1}")'''.format(prompt, language or 'unspecified')

# Singleton instance
auto_coding_service = AutoCodingService()
