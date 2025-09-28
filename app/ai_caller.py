import logging
import requests
import time
from typing import Dict, Tuple

class AICaller:
    """Ollama-only AI caller supporting streaming and non-streaming."""
    def __init__(self, model: str = "codellama", api_base: str = "http://localhost:11434", simulation_mode: bool = False):
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.simulation_mode = simulation_mode
        self.logger = logging.getLogger(__name__)
        
        if not simulation_mode:
            self._verify_connection()
        else:
            self.logger.info("🎭 AI Caller initialized in SIMULATION MODE")

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

    def call_model(self, prompt: Dict[str, str], stream: bool = False, max_tokens: int = 2048, temperature: float = 0.2) -> Tuple[str, int, int]:
        if not all(k in prompt for k in ["system", "user"]):
            raise KeyError("Prompt must contain 'system' and 'user' keys")
            
        if self.simulation_mode:
            return self._simulate_ai_response(prompt)
            
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
    
    def _simulate_ai_response(self, prompt: Dict[str, str]) -> Tuple[str, int, int]:
        """Simulate a realistic AI response for testing purposes."""
        self.logger.info("🎭 Generating simulated AI response...")
        
        # Analyze the prompt to determine what kind of tests to generate
        user_prompt = prompt.get('user', '').lower()
        
        if 'calculator' in user_prompt or 'add' in user_prompt or 'subtract' in user_prompt:
            # Generate calculator-specific tests
            simulated_response = """```yaml
new_tests:
  - test_name: "test_subtract_functionality"
    test_code: |
      def test_subtract_functionality():
          \"\"\"Test the subtract function with various inputs.\"\"\"
          assert subtract(10, 5) == 5
          assert subtract(0, 5) == -5
          assert subtract(-5, -3) == -2
          assert subtract(100, 50) == 50
    
  - test_name: "test_multiply_functionality" 
    test_code: |
      def test_multiply_functionality():
          \"\"\"Test the multiply function.\"\"\"
          assert multiply(3, 4) == 12
          assert multiply(0, 5) == 0
          assert multiply(-2, 3) == -6
          assert multiply(2.5, 4) == 10.0
    
  - test_name: "test_divide_edge_cases"
    test_code: |
      def test_divide_edge_cases():
          \"\"\"Test divide function with edge cases.\"\"\"
          assert divide(10, 2) == 5.0
          assert divide(7, 2) == 3.5
          with pytest.raises(ValueError, match="Cannot divide by zero"):
              divide(5, 0)
    
  - test_name: "test_is_even_functionality"
    test_code: |
      def test_is_even_functionality():
          \"\"\"Test the is_even function.\"\"\"
          assert is_even(2) == True
          assert is_even(3) == False
          assert is_even(0) == True
          assert is_even(-4) == True
          assert is_even(-3) == False
    
  - test_name: "test_calculator_advanced_operations"
    test_code: |
      def test_calculator_advanced_operations():
          \"\"\"Test Calculator class with different operations.\"\"\"
          calc = Calculator()
          
          # Test subtraction
          result = calc.calculate('-', 10, 3)
          assert result == 7
          
          # Test multiplication  
          result = calc.calculate('*', 4, 5)
          assert result == 20
          
          # Test division
          result = calc.calculate('/', 15, 3)
          assert result == 5.0
          
          # Test history tracking
          history = calc.get_history()
          assert len(history) == 3
          assert "10 - 3 = 7" in history[0]
          assert "4 * 5 = 20" in history[1]
          assert "15 / 3 = 5.0" in history[2]
    
  - test_name: "test_calculator_error_handling"
    test_code: |
      def test_calculator_error_handling():
          \"\"\"Test Calculator error handling.\"\"\"
          calc = Calculator()
          
          # Test invalid operation
          with pytest.raises(ValueError, match="Unknown operation"):
              calc.calculate('%', 5, 2)
          
          # Test division by zero
          with pytest.raises(ValueError, match="Cannot divide by zero"):
              calc.calculate('/', 10, 0)
```"""
        else:
            # Generic test response for other files
            simulated_response = """```yaml
new_tests:
  - test_name: "test_basic_functionality"
    test_code: |
      def test_basic_functionality():
          \"\"\"Test basic functionality of the module.\"\"\"
          # Add your test implementation here
          assert True
    
  - test_name: "test_edge_cases"
    test_code: |
      def test_edge_cases():
          \"\"\"Test edge cases and error handling.\"\"\"
          # Add your test implementation here
          assert True
```"""
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Count tokens (simulate)
        prompt_text = f"{prompt.get('system', '')}\n{prompt.get('user', '')}"
        prompt_tokens = self._count_tokens(prompt_text)
        completion_tokens = self._count_tokens(simulated_response)
        
        self.logger.info(f"🎭 Generated {completion_tokens} tokens in simulated response")
        
        return simulated_response, prompt_tokens, completion_tokens
    
    def test_connection(self) -> bool:
        """Test if the AI service is available."""
        if self.simulation_mode:
            self.logger.info("🎭 Simulation mode - connection test passed")
            return True
            
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
