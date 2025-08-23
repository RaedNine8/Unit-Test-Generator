import os
import subprocess
import logging
import shutil
from typing import Optional
from app.coverage_processor import CoverageProcessor

class UnitTestValidator:
    """
    Validates generated unit tests by running them and checking for coverage increase.
    Rolls back tests if they do not increase coverage.
    """
    def __init__(self, source_file_path: str, test_file_path: str, test_command: str, test_command_dir: str = ".", logger: Optional[logging.Logger] = None):
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.test_command = test_command
        self.test_command_dir = test_command_dir
        self.logger = logger or logging.getLogger(__name__)

    def run_tests(self) -> tuple[int, str, str]:
        """Run the test command and return (exit_code, stdout, stderr)."""
        self.logger.info(f"Running tests: {self.test_command} in {self.test_command_dir}")
        proc = subprocess.Popen(self.test_command, shell=True, cwd=self.test_command_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc.returncode, out.decode(), err.decode()

    def get_coverage(self) -> float:
        """Stub: Implement logic to parse coverage from a file or output."""
        # For now, just return a dummy value. You should parse your coverage report here.
        return 0.0

    def validate_and_rollback(self, old_coverage: float) -> bool:
        """
        Run tests, check for coverage increase, and roll back if not increased.
        Returns True if coverage increased, False if rolled back.
        """
        # Backup test file
        backup_path = self.test_file_path + ".bak"
        shutil.copyfile(self.test_file_path, backup_path)
        code, out, err = self.run_tests()
        if code != 0:
            self.logger.warning(f"Tests failed. Output:\n{out}\nErrors:\n{err}")
            shutil.move(backup_path, self.test_file_path)
            return False
        # Use CoverageProcessor to get new coverage
        coverage_report = os.path.join(self.test_command_dir, "coverage.xml")
        cp = CoverageProcessor(coverage_report, self.source_file_path)
        new_coverage = cp.get_coverage() or 0.0
        if new_coverage > old_coverage:
            self.logger.info(f"Coverage increased: {old_coverage} -> {new_coverage}")
            os.remove(backup_path)
            return True
        else:
            self.logger.info(f"Coverage did not increase. Rolling back test file.")
            shutil.move(backup_path, self.test_file_path)
            return False
