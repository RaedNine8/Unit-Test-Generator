## trying to test the AI CALL FOR OLLAM
from llm_handler import AICaller
import argparse
import sys
from typing import Optional, Tuple
from llm_handler.AICaller import AICaller
from config.Runner import Runner

##exemple of a simple command to use as a reference 
#U-GEN \
  #--source-file-path "app.go" \
  #--test-file-path "app_test.go" \
  #--code-coverage-report-path "coverage.xml" \
  #--test-command "go test -coverprofile=coverage.out && gocov convert coverage.out | gocov-xml > coverage.xml" \
  #--test-command-dir $(pwd) \
  #--coverage-type "cobertura" \
  #--desired-coverage 70 \
  #--max-iterations 1


class TestGenerator:
    def __init__(self, model: str = "codellama", api_base: str = "http://localhost:11434"):
        """Initialize test generator with model configuration"""
        self.ai_caller = AICaller(
            model=model,
            api_base=api_base,
            enable_retry=True
        )
        self.runner = Runner()

    def generate_test(self, prompt: dict) -> Tuple[str, int, int]:
        """Generate test using AI model"""
        try:
            return self.ai_caller.call_model(
                prompt=prompt,
                max_tokens=4096,
                stream=True
            )
        except Exception as e:
            print(f"Error generating test: {e}")
            return "", 0, 0

    def validate_test(self, test_code: str, working_dir: Optional[str] = None) -> bool:
        """Run generated test to validate it"""
        stdout, stderr, exit_code, _ = self.runner.run_command(
            command=f"python -m pytest -v",
            cwd=working_dir
        )
        return exit_code == 0, stdout, stderr

def main():
    parser = argparse.ArgumentParser(description='Generate and run tests using AI')
    parser.add_argument('--model', default='codellama', help='Model name')
    parser.add_argument('--api-base', default='http://localhost:11434', help='API base URL')
    parser.add_argument('--prompt', required=True, help='Test generation prompt')
    args = parser.parse_args()

    # Initialize test generator
    generator = TestGenerator(
        model=args.model,
        api_base=args.api_base
    )

    # Prepare prompt
    prompt = {
        "system": "You are a test generation assistant.",
        "user": args.prompt
    }

    # Generate test
    print("Generating test...")
    test_code, prompt_tokens, completion_tokens = generator.generate_test(prompt)
    
    if not test_code:
        print("Failed to generate test")
        sys.exit(1)

    # Validate test
    print("\nValidating generated test...")
    success, stdout, stderr = generator.validate_test(test_code)
    
    if success:
        print("\nTest validation successful!")
        print(f"Test code:\n{test_code}")
    else:
        print("\nTest validation failed!")
        print(f"stdout:\n{stdout}")
        print(f"stderr:\n{stderr}")

if __name__ == "__main__":
    main()