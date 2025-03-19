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

def main():
    args = parse_args()
    
    # Initialize components
    prompt_builder = PromptBuilder(
        source_file_path=args.source_file_path,
        test_file_path=args.test_file_path,
        code_coverage_report=args.code_coverage_report_path or "",
        included_files=args.included_files or "",
        project_root=args.project_root
    )
    
    ai_caller = AICaller(
        model=get_settings().get("llm.model", "deepseek-r1:8b"),
        api_base=get_settings().get("llm.api_base", "http://localhost:11434"),
        enable_retry=True
    )
    
    runner = Runner()
    
    current_coverage = 0.0
    iteration = 0
    
    while current_coverage < args.desired_coverage and iteration < args.max_iterations:
        print(f"\nIteration {iteration + 1}/{args.max_iterations}")
        
        success, stdout, stderr = run_test_iteration(
            prompt_builder=prompt_builder,
            ai_caller=ai_caller,
            runner=runner,
            test_command=args.test_command,
            test_dir=args.test_command_dir
        )
        
        if not success:
            print(f"Test run failed:\nstdout:{stdout}\nstderr:{stderr}")
            prompt_builder.failed_test_runs += f"\nIteration {iteration + 1} failed:\n{stderr}"
        
        # Update coverage if report exists
        if args.code_coverage_report_path:
            try:
                with open(args.code_coverage_report_path, 'r') as f:
                    # Simple coverage parsing - adapt based on coverage format
                    current_coverage = float(f.read().strip())
            except Exception as e:
                print(f"Error reading coverage report: {e}")
        
        iteration += 1
        
        print(f"Current coverage: {current_coverage}%")
    
    if current_coverage >= args.desired_coverage:
        print(f"Success! Achieved {current_coverage}% coverage")
        return 0
    else:
        print(f"Failed to achieve desired coverage. Current: {current_coverage}%")
        return 1

if __name__ == "__main__":
    sys.exit(main())