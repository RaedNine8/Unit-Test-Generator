import argparse
import sys
from pathlib import Path
from typing import Optional

from llm_handler.PromptBuilder import PromptBuilder
from llm_handler.AICaller import AICaller
from config.Runner import Runner
from config.settings.config_factory import get_settings

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


def parse_args():
    parser = argparse.ArgumentParser(description='Generate unit tests using LLM')
    parser.add_argument('--source-file-path', required=True, help='Path to source file')
    parser.add_argument('--test-file-path', required=True, help='Path to test file')
    parser.add_argument('--project-root', required=True, help='Project root directory')
    parser.add_argument('--code-coverage-report-path', help='Path to coverage report')
    parser.add_argument('--test-command', default='pytest', help='Test command to run')
    parser.add_argument('--test-command-dir', help='Directory to run test command')
    parser.add_argument('--coverage-type', default='pytest-cov', help='Type of coverage report')
    parser.add_argument('--desired-coverage', type=float, default=80.0, help='Desired coverage percentage')
    parser.add_argument('--max-iterations', type=int, default=3, help='Maximum LLM iterations')
    parser.add_argument('--included-files', help='Additional files to include')
    return parser.parse_args()

def run_test_iteration(
    prompt_builder: PromptBuilder,
    ai_caller: AICaller,
    runner: Runner,
    test_command: str,
    test_dir: Optional[str] ) -> tuple[bool, str, str]:
    # Generate prompt and get LLM response
    prompt = prompt_builder.build_prompt()
    response, _, _ = ai_caller.call_model(prompt=prompt)
    
    # Run tests
    stdout, stderr, exit_code, _ = runner.run_command(
        command=test_command,
        cwd=test_dir
    )
    
    return exit_code == 0, stdout, stderr

