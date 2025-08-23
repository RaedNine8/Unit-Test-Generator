
import logging
import subprocess
import os
from pathlib import Path

class TestRunner:
    """Handles running tests and processing results"""

    def __init__(self, test_command, test_command_dir):
        self.test_command = test_command
        self.test_command_dir = test_command_dir
        self.logger = logging.getLogger(__name__)

    def run_tests(self):
        """Run the test command and capture output"""
        self.logger.info(f"Running tests with command: '{self.test_command}' in '{self.test_command_dir}'")
        try:
            process = subprocess.run(
                self.test_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.test_command_dir,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.returncode
            
            if exit_code != 0:
                self.logger.warning(f"Test command exited with code {exit_code}")
                self.logger.debug(f"STDOUT:\n{stdout}")
                self.logger.debug(f"STDERR:\n{stderr}")
            else:
                self.logger.info("Test command executed successfully.")
            
            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            }
            
        except FileNotFoundError:
            self.logger.error(f"Test command not found: '{self.test_command.split()[0]}'")
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Command not found"}
        except Exception as e:
            self.logger.error(f"Error running test command: {e}", exc_info=True)
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}
