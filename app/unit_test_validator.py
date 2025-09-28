# filepath: c:\Users\raedn\OneDrive\Bureau\FILES\DEV FILES\PROJECT\U-GEN\Unit_Test_Generator\app\unit_test_validator_fixed.py

import os
import shutil
import logging
import datetime
import json
import subprocess
from typing import Optional, Dict, Any, List, Union

from abstract.prompt_builder_abc import PromptBuilderABC
from app.coverage_processor import CoverageProcessor
from app.logging.custom_logger import CustomLogger
from file_preprocessor import FilePreprocessor
from runner import Runner
from config.config_loader import get_settings
from config.config_schema import CoverageType
from utility.utils import load_yaml


class UnitTestValidator:
    """Simplified version of UnitTestValidator without external dependencies."""
    
    def __init__(
        self,
        source_file_path: str,
        test_file_path: str,
        code_coverage_report_path: str,
        test_command: str,
        llm_model: str,
        max_run_time_sec: int,
        agent_completion: PromptBuilderABC,
        desired_coverage: int,
        comparison_branch: str = "",
        coverage_type: CoverageType = "cobertura",
        diff_coverage: bool = False,
        num_attempts: int = 3,
        test_command_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        project_root: Optional[str] = None,
        generate_log_files: bool = True,
    ):
        """Initialize the UnitTestValidator with simplified parameters."""
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.code_coverage_report_path = code_coverage_report_path
        self.test_command = test_command
        self.llm_model = llm_model
        self.max_run_time_sec = max_run_time_sec
        self.agent_completion = agent_completion
        self.desired_coverage = desired_coverage
        self.comparison_branch = comparison_branch
        self.coverage_type = coverage_type
        self.diff_coverage = diff_coverage
        self.num_attempts = num_attempts
        self.test_command_dir = test_command_dir or os.path.dirname(self.test_file_path)
        self.project_root = project_root or os.getcwd()
        self.generate_log_files = generate_log_files
        
        # Initialize logger
        self.logger = logger or CustomLogger.get_logger(__name__, generate_log_files=generate_log_files)
        
        # Initialize components
        self.coverage_processor = CoverageProcessor(
            coverage_type=coverage_type,
            logger=self.logger
        )
        self.runner = Runner(
            command=test_command,
            cwd=self.test_command_dir,
            logger=self.logger
        )
        
        # State tracking
        self.current_coverage = 0.0
        self.last_coverage_percentages = {}
        self.last_source_file_coverage = 0.0
        self.failed_test_runs = []
        
    def get_coverage(self) -> float:
        """Get the current coverage percentage."""
        try:
            coverage_data = self.coverage_processor.process_coverage_report(
                self.code_coverage_report_path
            )
            
            if isinstance(coverage_data, dict) and 'total_coverage' in coverage_data:
                return coverage_data['total_coverage']
            elif isinstance(coverage_data, dict):
                # Calculate total coverage from file data
                total_lines = 0
                covered_lines = 0
                
                for file_path, file_data in coverage_data.items():
                    if isinstance(file_data, (list, tuple)) and len(file_data) >= 2:
                        covered, total = file_data[0], file_data[0] + file_data[1]
                        covered_lines += covered
                        total_lines += total
                
                return covered_lines / total_lines if total_lines > 0 else 0.0
            else:
                self.logger.warning("Unexpected coverage data format")
                return 0.0
                
        except Exception as e:
            self.logger.warning(f"Error getting coverage: {e}")
            return 0.0
    
    def get_language_extension_mapping(self) -> Dict[str, List[str]]:
        """Get language to file extension mapping from configuration."""
        try:
            settings = get_settings()
            default_settings = settings.get("default", {})
            language_extension_map = default_settings.get("language_extension_map", {})
            
            # Convert to standard dict format
            result = {}
            if hasattr(language_extension_map, 'items'):
                for language, extensions in language_extension_map.items():
                    if isinstance(extensions, (list, tuple)):
                        result[language] = list(extensions)
                    else:
                        result[language] = [str(extensions)]
            
            # Default mapping if none found
            if not result:
                result = {
                    "python": [".py"],
                    "javascript": [".js", ".jsx", ".ts", ".tsx"]
                }
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading language extension mapping: {e}")
            return {
                "python": [".py"],
                "javascript": [".js", ".jsx", ".ts", ".tsx"]
            }
    
    def run_test_command(self) -> Dict[str, Any]:
        """Run the test command and return the result."""
        try:
            self.logger.info(f'Running test command: "{self.test_command}"')
            
            result = subprocess.run(
                self.test_command,
                shell=True,
                cwd=self.test_command_dir,
                capture_output=True,
                text=True,
                timeout=self.max_run_time_sec
            )
            
            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Test command timed out after {self.max_run_time_sec} seconds")
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': 'Test command timed out',
                'success': False
            }
        except Exception as e:
            self.logger.error(f"Error running test command: {e}")
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def insert_test_into_file(self, test_code: str) -> bool:
        """Insert test code into the test file."""
        try:
            # Read existing test file
            if os.path.exists(self.test_file_path):
                with open(self.test_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            else:
                existing_content = ""
            
            # Simple insertion at the end of the file
            # In a more sophisticated version, we'd parse the AST and insert appropriately
            if existing_content:
                new_content = existing_content + "\n\n" + test_code
            else:
                new_content = test_code
            
            # Write back to file
            with open(self.test_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"Test inserted into {self.test_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inserting test into file: {e}")
            return False
    
    def validate_test(self, test_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate a single test by inserting it and running the test suite.
        
        Args:
            test_data: Dictionary containing test information
            
        Returns:
            Dictionary with validation results or None if validation failed
        """
        try:
            test_code = test_data.get('test_code', '')
            if not test_code:
                return {
                    'status': 'FAIL',
                    'reason': 'No test code provided',
                    'coverage_improvement': 0.0
                }
            
            # Backup current test file
            backup_path = self.test_file_path + '.backup'
            if os.path.exists(self.test_file_path):
                shutil.copy2(self.test_file_path, backup_path)
            
            # Get baseline coverage
            baseline_result = self.run_test_command()
            if not baseline_result['success']:
                self.logger.warning("Baseline test run failed")
            
            baseline_coverage = self.get_coverage()
            
            # Insert the new test
            if not self.insert_test_into_file(test_code):
                return {
                    'status': 'FAIL',
                    'reason': 'Failed to insert test code',
                    'coverage_improvement': 0.0
                }
            
            # Run tests with new test
            test_result = self.run_test_command()
            
            if test_result['success']:
                new_coverage = self.get_coverage()
                coverage_improvement = new_coverage - baseline_coverage
                
                if coverage_improvement > 0:
                    self.logger.info(f"Test passed and improved coverage by {coverage_improvement:.2%}")
                    return {
                        'status': 'PASS',
                        'reason': 'Test passed and improved coverage',
                        'coverage_improvement': coverage_improvement,
                        'baseline_coverage': baseline_coverage,
                        'new_coverage': new_coverage
                    }
                else:
                    self.logger.info("Test passed but did not improve coverage")
                    # Restore backup
                    if os.path.exists(backup_path):
                        shutil.move(backup_path, self.test_file_path)
                    
                    return {
                        'status': 'FAIL',
                        'reason': 'Test did not improve coverage',
                        'coverage_improvement': coverage_improvement,
                        'baseline_coverage': baseline_coverage,
                        'new_coverage': new_coverage
                    }
            else:
                self.logger.warning("Test run failed")
                # Restore backup
                if os.path.exists(backup_path):
                    shutil.move(backup_path, self.test_file_path)
                
                return {
                    'status': 'FAIL',
                    'reason': 'Test execution failed',
                    'coverage_improvement': 0.0,
                    'error_output': test_result['stderr']
                }
                
        except Exception as e:
            self.logger.error(f"Error validating test: {e}")
            # Try to restore backup
            backup_path = self.test_file_path + '.backup'
            if os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, self.test_file_path)
                except Exception:
                    pass
            
            return {
                'status': 'FAIL',
                'reason': f'Validation error: {str(e)}',
                'coverage_improvement': 0.0
            }
        finally:
            # Clean up backup
            backup_path = self.test_file_path + '.backup'
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except Exception:
                    pass
    
    def process_failed_test_runs(self) -> None:
        """Process any failed test runs (simplified version)."""
        if self.failed_test_runs:
            self.logger.warning(f"There were {len(self.failed_test_runs)} failed test runs")
            for i, failure in enumerate(self.failed_test_runs[:3]):  # Log first 3
                self.logger.warning(f"Failed test {i+1}: {failure.get('reason', 'Unknown error')}")
    
    def get_coverage_percentages(self) -> Dict[str, float]:
        """Get coverage percentages for individual files."""
        try:
            coverage_data = self.coverage_processor.process_coverage_report(
                self.code_coverage_report_path
            )
            
            if isinstance(coverage_data, dict):
                result = {}
                for file_path, file_data in coverage_data.items():
                    if isinstance(file_data, (list, tuple)) and len(file_data) >= 2:
                        covered, missed = file_data[0], file_data[1]
                        total = covered + missed
                        if total > 0:
                            result[file_path] = covered / total
                        else:
                            result[file_path] = 0.0
                    elif isinstance(file_data, (int, float)):
                        result[file_path] = float(file_data)
                
                return result
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting coverage percentages: {e}")
            return {}
