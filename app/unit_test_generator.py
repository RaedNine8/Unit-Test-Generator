import os
import re
import logging
from typing import Dict, Any

class UnitTestGenerator:
    """Simplified test generator for Python and JavaScript only"""
    
    def __init__(self, ai_caller, test_runner, language, source_file_path, test_file_path):
        self.ai_caller = ai_caller
        self.test_runner = test_runner
        self.language = language
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.logger = logging.getLogger(__name__)
        
    def generate_tests(self, max_iterations: int) -> Dict[str, Any]:
        """Generate tests for the specified source file."""
        results = {
            'tests_generated': 0,
            'tests_passed': 0,
            'iterations_used': 0,
            'generated_tests': []
        }
        
        for iteration in range(max_iterations):
            results['iterations_used'] = iteration + 1
            self.logger.info(f"Iteration {iteration + 1}/{max_iterations}")
            
            # Generate a new test
            test_code = self.generate_single_test()
            
            if test_code:
                # Add the new test to the test file
                if self.add_test_to_file(test_code):
                    results['tests_generated'] += 1
                    
                    # Run the tests
                    test_results = self.test_runner.run_tests()
                    if test_results['success']:
                        self.logger.info("Generated test passed.")
                        results['tests_passed'] += 1
                        results['generated_tests'].append(test_code)
                    else:
                        self.logger.warning("Generated test failed. Removing it.")
                        self.remove_last_test(test_code)
        
        return results
    
    def generate_single_test(self) -> str | None:
        """Generate a single test using the AI caller."""
        source_code = self.read_file_content(self.source_file_path)
        existing_tests = self.read_file_content(self.test_file_path)
        
        prompt = self.build_test_prompt(source_code, existing_tests)
        
        try:
            response = self.ai_caller.call(prompt)
            return self.extract_test_code(response)
        except Exception as e:
            self.logger.error(f"Error calling AI: {e}", exc_info=True)
            return None

    def build_test_prompt(self, source_code: str, existing_tests: str) -> str:
        """Build the prompt for the AI model."""
        if self.language == 'python':
            framework = 'pytest'
        else:
            framework = 'jest' # Assuming jest for javascript

        prompt = (
            f"You are an expert {self.language} programmer specializing in writing unit tests with {framework}.\n"
            f"Your task is to write a new, unique, and meaningful unit test for the given source code.\n"
            f"Do not repeat any of the existing tests.\n\n"
            f"Source Code:\n```\n{source_code}\n```\n\n"
            f"Existing Tests:\n```\n{existing_tests}\n```\n\n"
            f"Please provide only the new test code, without any explanations or markdown formatting."
        )
        return prompt

    def extract_test_code(self, response: str) -> str:
        """Extract the test code from the AI's response."""
        # This might need to be adjusted based on the model's output format
        code_match = re.search(r"```(?:python|javascript)?\n(.*?)```", response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return response.strip()

    def add_test_to_file(self, test_code: str) -> bool:
        """Append the generated test to the test file."""
        try:
            with open(self.test_file_path, 'a') as f:
                f.write('\n\n' + test_code)
            self.logger.info(f"Appended new test to {self.test_file_path}")
            return True
        except IOError as e:
            self.logger.error(f"Error writing to test file: {e}")
            return False

    def remove_last_test(self, test_code: str):
        """Remove the last added test from the test file."""
        try:
            with open(self.test_file_path, 'r') as f:
                content = f.read()
            # Remove the last occurrence of the test code
            updated_content = content.rstrip().rsplit(test_code, 1)[0].rstrip()
            with open(self.test_file_path, 'w') as f:
                f.write(updated_content)
            self.logger.info("Removed last generated test from test file.")
        except Exception as e:
            self.logger.error(f"Error removing last test: {e}")

    def read_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return ""