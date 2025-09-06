import logging
import requests
import time
from typing import Dict, Tuple

class AICaller:
    """Ollama-only AI caller supporting streaming and non-streaming."""
    def __init__(self, model: str = "codellama", api_base: str = "http://localhost:11434"):
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self._verify_connection()

    def _verify_connection(self):
        self.logger.info(f"Verifying connection to Ollama at {self.api_base}...")
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            if f"{self.model}:latest" not in model_names:
                self.logger.warning(f"Model '{self.model}' not found in Ollama.")
                self.logger.info(f"Available models: {', '.join(model_names)}")
                self.logger.info(f"You can pull the model by running: ollama pull {self.model}")
        except Exception as e:
            self.logger.error(f"Could not connect to Ollama at {self.api_base}: {e}")
            raise

    def call(self, prompt: Dict[str, str], stream: bool = False, max_tokens: int = 2048, temperature: float = 0.2) -> Tuple[str, int, int]:
        if not all(k in prompt for k in ["system", "user"]):
            raise KeyError("Prompt must contain 'system' and 'user' keys")
        message = f"{prompt['system']}\n\n{prompt['user']}" if prompt['system'] else prompt['user']
        payload = {
            "model": self.model,
            "prompt": message,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        try:
            if stream:
                return self._handle_streaming(payload, message)
            else:
                return self._handle_non_streaming(payload, message)
        except Exception as e:
            self.logger.error(f"Error during Ollama call: {e}")
            raise

    def _handle_streaming(self, payload: Dict, original_prompt: str) -> Tuple[str, int, int]:
        response = requests.post(f"{self.api_base}/api/generate", json=payload, stream=True)
        response.raise_for_status()
        full_response = ""
        print("Streaming results from LLM model...")
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                print(chunk, end='', flush=True)
                full_response += chunk
                time.sleep(0.01)
        print("\n")
        prompt_tokens = self._count_tokens(original_prompt)
        completion_tokens = self._count_tokens(full_response)
        return full_response, prompt_tokens, completion_tokens

    def _handle_non_streaming(self, payload: Dict, original_prompt: str) -> Tuple[str, int, int]:
        response = requests.post(f"{self.api_base}/api/generate", json=payload)
        response.raise_for_status()
        content = response.json().get('response', '')
        print(f"Printing results from LLM model...\n{content}")
        prompt_tokens = self._count_tokens(original_prompt)
        completion_tokens = self._count_tokens(content)
        return content, prompt_tokens, completion_tokens

    def _count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
