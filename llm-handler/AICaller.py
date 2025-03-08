import datetime
import os
import time
import requests
from functools import wraps
from typing import Dict, Tuple, Optional
from tenacity import retry, stop_after_attempt, wait_fixed

MODEL_RETRIES = 3

def conditional_retry(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.enable_retry:
            return func(self, *args, **kwargs)

        @retry(
            stop=stop_after_attempt(MODEL_RETRIES),
            wait=wait_fixed(1)
        )
        def retry_wrapper():
            return func(self, *args, **kwargs)
        return retry_wrapper()
    return wrapper

class AICaller:
    def __init__(self, model: str, api_base: str, enable_retry: bool = True):
        """
        Initialize API caller for LLM models.
        
        Args:
            model: Model name
            api_base: Base URL for API calls
            enable_retry: Enable retry mechanism
        """
        self.model = model
        self.api_base = api_base.rstrip('/')
        self.enable_retry = enable_retry
        self.session = requests.Session()

    def _count_tokens(self, text: str) -> int:
        """Approximate token count - 4 chars per token"""
        return len(text) // 4

    def _prepare_messages(self, prompt: Dict[str, str]) -> str:
        """Prepare messages for API call"""
        if not all(k in prompt for k in ['system', 'user']):
            raise KeyError("Prompt must contain 'system' and 'user' keys")
        
        combined = f"{prompt['system']}\n\n{prompt['user']}" if prompt['system'] else prompt['user']
        return combined

    def _make_request(self, payload: Dict, stream: bool = False) -> requests.Response:
        """Make HTTP request to API"""
        headers = {'Content-Type': 'application/json'}
        url = f"{self.api_base}/api/generate"
        
        response = self.session.post(
            url,
            json=payload,
            headers=headers,
            stream=stream
        )
        response.raise_for_status()
        return response

    @conditional_retry
    def call_model(self, prompt: Dict[str, str], max_tokens: int = 4096, stream: bool = True) -> Tuple[str, int, int]:
        """
        Call LLM model with prompt.
        
        Args:
            prompt: Dictionary with system and user prompts
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Tuple of (response_text, prompt_tokens, completion_tokens)
        """
        message = self._prepare_messages(prompt)
        
        payload = {
            "model": self.model,
            "prompt": message,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": stream
        }

        try:
            if stream:
                return self._handle_streaming(payload, message)
            else:
                return self._handle_non_streaming(payload, message)
                
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {str(e)}")
            raise

    def _handle_streaming(self, payload: Dict, original_prompt: str) -> Tuple[str, int, int]:
        """Handle streaming response"""
        response = self._make_request(payload, stream=True)
        chunks = []
        full_response = ""
        
        print("Streaming results from LLM model...")
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                print(chunk, end='', flush=True)
                chunks.append(chunk)
                full_response += chunk
                time.sleep(0.01)
        
        print("\n")
        prompt_tokens = self._count_tokens(original_prompt)
        completion_tokens = self._count_tokens(full_response)
        
        return full_response, prompt_tokens, completion_tokens

    def _handle_non_streaming(self, payload: Dict, original_prompt: str) -> Tuple[str, int, int]:
        """Handle non-streaming response"""
        response = self._make_request(payload, stream=False)
        content = response.json()['response']
        
        print(f"Printing results from LLM model...\n{content}")
        
        prompt_tokens = self._count_tokens(original_prompt)
        completion_tokens = self._count_tokens(content)
        
        return content, prompt_tokens, completion_tokens