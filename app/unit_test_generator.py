# filepath: c:\Users\raedn\OneDrive\Bureau\FILES\DEV FILES\PROJECT\U-GEN\Unit_Test_Generator\app\unit_test_generator_fixed.py

import json
import os
import logging
from typing import Optional, Dict, Any, List

from abstract.prompt_builder_abc import PromptBuilderABC
from app.logging.custom_logger import CustomLogger
from file_preprocessor import FilePreprocessor
from config.config_loader import get_settings
from utility.utils import load_yaml


class UnitTestGenerator:
    """Simplified version of UnitTestGenerator with fixed imports and types."""
    
    def __init__(
        self,
        source_file_path: str,
        test_file_path: str,
        code_coverage_report_path: str,
        test_command: str,
        llm_model: str,
        agent_completion: PromptBuilderABC,
        test_command_dir: str = os.getcwd(),
        included_files: Optional[List[str]] = None,
        coverage_type: str = "cobertura",
        additional_instructions: str = "",
        use_report_coverage_feature_flag: bool = False,
        project_root: str = "",
        logger: Optional[logging.Logger] = None,
        generate_log_files: bool = True,
    ):
        """Initialize the UnitTestGenerator with simplified parameters."""
        self.project_root = project_root or os.getcwd()
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.code_coverage_report_path = code_coverage_report_path
        self.test_command = test_command
        self.test_command_dir = test_command_dir
        self.included_files = included_files or []
        self.coverage_type = coverage_type
        self.additional_instructions = additional_instructions
        self.language = self.get_code_language(source_file_path)
        self.use_report_coverage_feature_flag = use_report_coverage_feature_flag
        self.last_coverage_percentages = {}
        self.llm_model = llm_model
        self.agent_completion = agent_completion
        self.generate_log_files = generate_log_files

        # Get the logger instance (returns standard logging.Logger)
        self.logger = logger or CustomLogger.get_logger(__name__, generate_log_files=generate_log_files)

        # States to maintain within this class
        self.preprocessor = FilePreprocessor(self.test_file_path)
        self.total_input_token_count = 0
        self.total_output_token_count = 0
        self.testing_framework = "Unknown"
        self.code_coverage_report = ""

        # Read source file
        try:
            with open(self.source_file_path, "r", encoding="utf-8") as f:
                self.source_code = f.read()
        except Exception as e:
            self.logger.error(f"Error reading source file {self.source_file_path}: {e}")
            self.source_code = ""

        # Read or create test file
        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                self.test_code = f.read()
        except FileNotFoundError:
            # Create empty test file if it doesn't exist
            self.test_code = ""
            try:
                with open(self.test_file_path, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception as e:
                self.logger.error(f"Error creating test file {self.test_file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error reading test file {self.test_file_path}: {e}")
            self.test_code = ""

    def get_code_language(self, source_file_path: str) -> str:
        """Get the programming language based on file extension."""
        # Get file extension
        extension_s = "." + source_file_path.rsplit(".")[-1].lower() if "." in source_file_path else ""
        
        # Simple mapping for supported languages
        extension_to_language = {
            ".py": "python",
            ".js": "javascript", 
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript"
        }
        
        return extension_to_language.get(extension_s, "unknown")

    def check_for_failed_test_runs(self, failed_test_runs: Optional[List[Dict[str, Any]]]) -> str:
        """Process failed test runs and return formatted string."""
        if not failed_test_runs:
            return ""
        
        failed_test_runs_value = ""
        try:
            for failed_test in failed_test_runs:
                failed_test_dict = failed_test.get("code", {})
                if not failed_test_dict:
                    continue
                
                # Convert dict to string
                code = json.dumps(failed_test_dict, indent=2)
                error_message = failed_test.get("error_message", None)
                failed_test_runs_value += f"Failed Test:\n```\n{code}\n```\n"
                if error_message:
                    failed_test_runs_value += f"Test execution error analysis:\n{error_message}\n\n\n"
                else:
                    failed_test_runs_value += "\n\n"
        except Exception as e:
            self.logger.error(f"Error processing failed test runs: {e}")
            failed_test_runs_value = ""

        return failed_test_runs_value

    def get_max_tests_per_run(self) -> int:
        """Get max tests per run from settings with proper error handling."""
        try:
            settings = get_settings()
            # Try different access patterns for dynaconf
            if hasattr(settings, 'default') and hasattr(settings.default, 'max_tests_per_run'):
                return int(settings.default.max_tests_per_run)
            elif hasattr(settings, 'max_tests_per_run'):
                return int(settings.max_tests_per_run)
            else:
                return 4
        except Exception:
            return 4

    def get_included_files_content(self) -> str:
        """Convert included files to string format."""
        if not self.included_files:
            return ""
        
        try:
            from utility.utils import get_included_files
            return get_included_files(self.included_files, self.project_root)
        except Exception as e:
            self.logger.warning(f"Error getting included files: {e}")
            return ""

    def generate_tests(
        self, 
        failed_test_runs: Optional[List[Dict[str, Any]]] = None, 
        language: str = "", 
        testing_framework: str = "", 
        code_coverage_report: str = ""
    ) -> Dict[str, Any]:
        """
        Generate tests using the AI model based on the constructed prompt.
        
        Returns:
            Dict containing generated tests or empty dict if error occurs
        """
        # Process failed test runs
        failed_test_runs_value = self.check_for_failed_test_runs(failed_test_runs)
        
        # Get max tests per run
        max_tests_per_run = self.get_max_tests_per_run()
        
        # Get included files content
        additional_includes_section = self.get_included_files_content()
        
        # Use provided language or fall back to detected language
        language = language or self.language
        
        try:
            # Generate tests using the agent completion
            response, prompt_token_count, response_token_count, self.prompt = self.agent_completion.generate_tests(
                source_file_name=os.path.relpath(self.source_file_path, self.project_root),
                max_tests=max_tests_per_run,
                source_file_numbered="\n".join(f"{i + 1} {line}" for i, line in enumerate(self.source_code.split("\n"))),
                code_coverage_report=code_coverage_report,
                additional_instructions_text=self.additional_instructions,
                additional_includes_section=additional_includes_section,
                language=language,
                test_file=self.test_code,
                failed_tests_section=failed_test_runs_value,
                test_file_name=os.path.relpath(self.test_file_path, self.project_root),
                testing_framework=testing_framework,
            )

            # Update token counts
            self.total_input_token_count += prompt_token_count
            self.total_output_token_count += response_token_count
            
            # Parse the response
            tests_dict = load_yaml(
                response,
                keys_fix_yaml=["test_tags", "test_code", "test_name", "test_behavior"],
            )
            
            if tests_dict is None:
                self.logger.warning("No tests were generated from AI response")
                return {}
                
            return tests_dict
            
        except Exception as e:
            self.logger.error(f"Error during test generation: {e}")
            # Return empty dict instead of trying to record failure
            return {}
