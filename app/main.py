import argparse
import os
import logging
from pathlib import Path
from ai_caller import AICaller
from unit_test_generator import UnitTestGenerator
from runner import Runner
from app.database import initialize_database

def setup_logger(log_level="INFO", log_file=None):
    """Setup simplified logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments - simplified version"""
    parser = argparse.ArgumentParser(description="Simplified Test Generation Tool")
    
    # Required arguments
    parser.add_argument("--source-file-path", required=True, help="Path to source file")
    parser.add_argument("--test-file-path", required=True, help="Path to test file")
    parser.add_argument("--test-command", required=True, help="Command to run tests")
    
    # Optional arguments
    parser.add_argument("--test-command-dir", default=".", help="Directory to run test command")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum LLM iterations")
    
    # Ollama specific
    parser.add_argument("--model", default="codellama", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    
    # Simplified options
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--language", choices=["python", "javascript"], help="Programming language (auto-detected if not specified)")
    
    return parser.parse_args()

def detect_language(file_path):
    """Detect programming language from file extension"""
    ext = Path(file_path).suffix.lower()
    if ext in ['.py']:
        return 'python'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return 'javascript'
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Only Python and JavaScript are supported.")

def main():
    """Main entry point - simplified version"""
    args = parse_args()
    
    # Setup logging
    logger = setup_logger(args.log_level)
    logger.info("Starting Simplified Test Generator")

    # Initialize the database
    initialize_database()
    
    # Auto-detect language if not specified
    if not args.language:
        args.language = detect_language(args.source_file_path)
        logger.info(f"Detected language: {args.language}")
    
    # Verify files exist
    if not os.path.exists(args.source_file_path):
        logger.error(f"Source file not found: {args.source_file_path}")
        return 1
    
    if not os.path.exists(args.test_file_path):
        logger.warning(f"Test file not found: {args.test_file_path}. Will create it.")
        Path(args.test_file_path).touch()
    
    try:
        # Initialize Ollama caller
        logger.info(f"Initializing Ollama with model: {args.model}")
        ai_caller = AICaller(
            model=args.model,
            api_base=args.ollama_url
        )
        
        # Initialize test runner
        test_runner = Runner(
            test_command=args.test_command,
            test_command_dir=args.test_command_dir
        )
        
        # Initialize test generator
        test_generator = UnitTestGenerator(
            ai_caller=ai_caller,
            test_runner=test_runner,
            language=args.language,
            source_file_path=args.source_file_path,
            test_file_path=args.test_file_path
        )
        
        # Run test generation
        logger.info("Starting test generation...")
        results = test_generator.generate_tests(max_iterations=args.max_iterations)

        # Log results to database
        from app.database import log_test_run
        log_test_run(
            source_file=args.source_file_path,
            tests_generated=results['tests_generated'],
            tests_passed=results['tests_passed']
        )

        logger.info("=" * 50)
        logger.info("TEST GENERATION COMPLETE")
        logger.info("=" * 50)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during test generation: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
