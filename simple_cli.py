#!/usr/bin/env python3
"""
Simple CLI entry point for the Simplified Cover Agent.
"""
import argparse
import os
import sys
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.cover_agent import CoverAgent
from app.logging.custom_logger import CustomLogger


def detect_language(file_path):
    """Detect language from file extension"""
    ext = Path(file_path).suffix.lower()
    if ext == '.py':
        return 'python'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return 'javascript'
    else:
        raise ValueError(f"Unsupported language for file: {file_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Simplified Cover Agent - Generate unit tests to improve code coverage"
    )
    
    # Required arguments
    parser.add_argument(
        "--source-file-path",
        required=True,
        help="Path to the source file to generate tests for"
    )
    parser.add_argument(
        "--test-file-path", 
        required=True,
        help="Path to the test file (will be created if doesn't exist)"
    )
    parser.add_argument(
        "--test-command",
        required=True,
        help="Command to run tests and generate coverage report"
    )
    
    # Optional arguments with defaults
    parser.add_argument(
        "--code-coverage-report-path",
        default="coverage.xml",
        help="Path to coverage report file (default: coverage.xml)"
    )
    parser.add_argument(
        "--model",
        default="deepseek-coder", 
        help="Ollama model name (default: deepseek-coder)"
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:11434",
        help="Ollama API base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--desired-coverage",
        type=int,
        default=70,
        help="Target coverage percentage (default: 70)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of iterations (default: 3)"
    )
    parser.add_argument(
        "--max-run-time-sec",
        type=int,
        default=30,
        help="Maximum test execution time in seconds (default: 30)"
    )
    parser.add_argument(
        "--test-command-dir",
        help="Directory to run test command in (default: test file directory)"
    )
    parser.add_argument(
        "--project-root",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = CustomLogger.get_logger(__name__)
    
    print("🚀 Simplified Cover Agent")
    print("=" * 50)
    
    # Verify source file exists
    if not os.path.exists(args.source_file_path):
        print(f"❌ Source file not found: {args.source_file_path}")
        return 1
    
    # Create test file if it doesn't exist
    if not os.path.exists(args.test_file_path):
        print(f"📝 Creating test file: {args.test_file_path}")
        Path(args.test_file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(args.test_file_path).touch()
    
    # Detect language
    try:
        language = detect_language(args.source_file_path)
        print(f"🔍 Detected language: {language}")
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    
    try:
        print(f"🤖 Using model: {args.model}")
        print(f"🎯 Target coverage: {args.desired_coverage}%")
        
        # Initialize Cover Agent
        agent = CoverAgent(
            source_file_path=args.source_file_path,
            test_file_path=args.test_file_path,
            code_coverage_report_path=args.code_coverage_report_path,
            test_command=args.test_command,
            model=args.model,
            api_base=args.api_base,
            desired_coverage=args.desired_coverage,
            max_iterations=args.max_iterations,
            max_run_time_sec=args.max_run_time_sec,
            test_command_dir=args.test_command_dir,
            project_root=args.project_root or os.getcwd(),
            logger=logger
        )
        
        # Run the agent
        success = agent.run()
        
        # Display final results
        print("\n" + "=" * 50)
        print("📊 FINAL RESULTS")
        print("=" * 50)
        
        if success:
            print("✅ SUCCESS: Target coverage achieved!")
        else:
            print("❌ DEMONSTRATION: This is a simplified version")
        
        print(f"📈 Final coverage: {agent.current_coverage * 100:.2f}%")
        print(f"🎯 Target coverage: {agent.desired_coverage}%")
        print(f"🧪 Tests generated: {agent.tests_generated}")
        print(f"✔️  Tests passed: {agent.tests_passed}")
        print(f"🔄 Iterations: {agent.iteration_count}")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {e}")
        logger.error(f"Main error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
