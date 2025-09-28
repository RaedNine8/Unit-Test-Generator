import xml.etree.ElementTree as ET
import json
import os
import time
import logging
from typing import Tuple, List, Dict, Optional, Union
from enum import Enum

from app.logging.custom_logger import CustomLogger


class CoverageType(Enum):
    COBERTURA = "cobertura"
    LCOV = "lcov" 
    JACOCO = "jacoco"
    DIFF_COVER_JSON = "diff_cover_json"


class CoverageProcessor:
    """
    Processes coverage reports and extracts coverage information.
    Supports multiple coverage formats but simplified for Python/JavaScript only.
    """
    
    def __init__(
        self,
        file_path: str,
        src_file_path: str,
        coverage_type: CoverageType,
        use_report_coverage_feature_flag: bool = False,
        diff_coverage_report_path: str = None,
        logger: Optional[CustomLogger] = None,
        generate_log_files: bool = True,
    ):
        """
        Initialize the CoverageProcessor.
        
        Args:
            file_path: Path to the coverage report file
            src_file_path: Path to the source file being analyzed
            coverage_type: Type of coverage report
            use_report_coverage_feature_flag: Whether to use report coverage feature
            diff_coverage_report_path: Path to diff coverage report
            logger: Optional logger instance
            generate_log_files: Whether to generate log files
        """
        self.file_path = file_path
        self.src_file_path = src_file_path
        self.coverage_type = coverage_type
        self.use_report_coverage_feature_flag = use_report_coverage_feature_flag
        self.diff_coverage_report_path = diff_coverage_report_path
        
        self.logger = logger or CustomLogger.get_logger(__name__, generate_log_files=generate_log_files)

    def process_coverage_report(self, time_of_test_command: int) -> Union[Tuple[List, List, float], Dict]:
        """
        Process the coverage report and extract coverage information.
        
        Args:
            time_of_test_command: Timestamp of when the test command was executed
            
        Returns:
            If use_report_coverage_feature_flag is True: Dict mapping file paths to coverage info
            Otherwise: Tuple of (lines_covered, lines_missed, percentage_covered)
        """
        # Verify the report was updated after the test command
        self.verify_report_update(time_of_test_command)
        
        if self.use_report_coverage_feature_flag:
            return self.parse_coverage_report()
        else:
            # Return coverage for just the source file
            lines_covered, lines_missed, percentage_covered = self._parse_single_file_coverage()
            return lines_covered, lines_missed, percentage_covered

    def verify_report_update(self, time_of_test_command: int):
        """Verify that the coverage report was updated after the test command."""
        if not os.path.exists(self.file_path):
            raise AssertionError(f"Coverage report not found: {self.file_path}")
            
        report_mtime = int(os.path.getmtime(self.file_path) * 1000)  # Convert to milliseconds
        
        if report_mtime < time_of_test_command:
            raise AssertionError(
                f"Coverage report was not updated after test command. "
                f"Report time: {report_mtime}, Test time: {time_of_test_command}"
            )

    def parse_coverage_report(self) -> Dict:
        """
        Parse the coverage report and return coverage info for all files.
        
        Returns:
            Dict mapping file paths to (lines_covered, lines_missed, percentage_covered) tuples
        """
        if self.coverage_type == CoverageType.COBERTURA:
            return self.parse_coverage_report_cobertura()
        elif self.coverage_type == CoverageType.LCOV:
            return self.parse_coverage_report_lcov()
        elif self.coverage_type == CoverageType.JACOCO:
            return self.parse_coverage_report_jacoco()
        elif self.coverage_type == CoverageType.DIFF_COVER_JSON:
            return self.parse_diff_coverage_report()
        else:
            raise NotImplementedError(f"Coverage type {self.coverage_type} not supported")

    def _parse_single_file_coverage(self) -> Tuple[List, List, float]:
        """Parse coverage for the specific source file."""
        if self.coverage_type == CoverageType.COBERTURA:
            return self._parse_cobertura_single_file()
        elif self.coverage_type == CoverageType.LCOV:
            return self._parse_lcov_single_file()
        elif self.coverage_type == CoverageType.JACOCO:
            return self._parse_jacoco_single_file()
        else:
            raise NotImplementedError(f"Coverage type {self.coverage_type} not supported")

    def parse_coverage_report_cobertura(self, filename: str = None) -> Union[Tuple[List, List, float], Dict]:
        """Parse Cobertura XML coverage report."""
        coverage_file = filename or self.file_path
        
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            if self.use_report_coverage_feature_flag:
                # Return coverage for all files
                file_coverage_dict = {}
                
                for cls in root.iter('class'):
                    filename = cls.get('filename')
                    if filename:
                        lines_covered, lines_missed, percentage = self.parse_coverage_data_for_class(cls)
                        file_coverage_dict[filename] = (lines_covered, lines_missed, percentage)
                        
                return file_coverage_dict
            else:
                # Return coverage for specific source file
                return self._parse_cobertura_single_file()
                
        except ET.ParseError as e:
            self.logger.error(f"Error parsing Cobertura XML: {e}")
            return {} if self.use_report_coverage_feature_flag else ([], [], 0.0)

    def _parse_cobertura_single_file(self) -> Tuple[List, List, float]:
        """Parse Cobertura coverage for a single file."""
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            
            # Find the class/file that matches our source file
            for cls in root.iter('class'):
                filename = cls.get('filename')
                if filename and self._file_matches(filename, self.src_file_path):
                    return self.parse_coverage_data_for_class(cls)
                    
            # If not found, return empty coverage
            self.logger.warning(f"Source file {self.src_file_path} not found in coverage report")
            return [], [], 0.0
            
        except Exception as e:
            self.logger.error(f"Error parsing Cobertura coverage: {e}")
            return [], [], 0.0

    def parse_coverage_data_for_class(self, cls) -> Tuple[List, List, float]:
        """Parse coverage data for a specific class element."""
        lines_covered = []
        lines_missed = []
        
        for line in cls.iter('line'):
            line_number = int(line.get('number', 0))
            hits = int(line.get('hits', 0))
            
            if hits > 0:
                lines_covered.append(line_number)
            else:
                lines_missed.append(line_number)
                
        total_lines = len(lines_covered) + len(lines_missed)
        percentage_covered = len(lines_covered) / total_lines if total_lines > 0 else 0.0
        
        return lines_covered, lines_missed, percentage_covered

    def parse_coverage_report_lcov(self) -> Dict:
        """Parse LCOV coverage report."""
        file_coverage_dict = {}
        
        try:
            with open(self.file_path, 'r') as f:
                current_file = None
                lines_covered = []
                lines_missed = []
                
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('SF:'):  # Source file
                        current_file = line[3:]  # Remove 'SF:' prefix
                        lines_covered = []
                        lines_missed = []
                        
                    elif line.startswith('DA:'):  # Line data
                        parts = line[3:].split(',')  # Remove 'DA:' prefix
                        if len(parts) >= 2:
                            line_num = int(parts[0])
                            hit_count = int(parts[1])
                            
                            if hit_count > 0:
                                lines_covered.append(line_num)
                            else:
                                lines_missed.append(line_num)
                                
                    elif line == 'end_of_record' and current_file:
                        total_lines = len(lines_covered) + len(lines_missed)
                        percentage = len(lines_covered) / total_lines if total_lines > 0 else 0.0
                        file_coverage_dict[current_file] = (lines_covered, lines_missed, percentage)
                        
        except Exception as e:
            self.logger.error(f"Error parsing LCOV report: {e}")
            
        return file_coverage_dict

    def _parse_lcov_single_file(self) -> Tuple[List, List, float]:
        """Parse LCOV coverage for a single file."""
        file_coverage = self.parse_coverage_report_lcov()
        
        for file_path, (lines_covered, lines_missed, percentage) in file_coverage.items():
            if self._file_matches(file_path, self.src_file_path):
                return lines_covered, lines_missed, percentage
                
        return [], [], 0.0

    def parse_coverage_report_jacoco(self) -> Union[Tuple[List, List, float], Dict]:
        """Parse JaCoCo coverage report (CSV format)."""
        # Note: JaCoCo support is minimal since we focus on Python/JavaScript
        self.logger.warning("JaCoCo support is limited in this implementation")
        return {} if self.use_report_coverage_feature_flag else ([], [], 0.0)

    def _parse_jacoco_single_file(self) -> Tuple[List, List, float]:
        """Parse JaCoCo coverage for a single file."""
        return [], [], 0.0

    def parse_diff_coverage_report(self) -> Dict:
        """Parse diff coverage JSON report."""
        if not self.diff_coverage_report_path or not os.path.exists(self.diff_coverage_report_path):
            self.logger.warning("Diff coverage report not found")
            return {}
            
        try:
            with open(self.diff_coverage_report_path, 'r') as f:
                data = json.load(f)
                
            file_coverage_dict = {}
            
            for file_path, file_data in data.get('src_stats', {}).items():
                covered_lines = file_data.get('covered_lines', [])
                missed_lines = file_data.get('missing_lines', [])
                
                total_lines = len(covered_lines) + len(missed_lines)
                percentage = len(covered_lines) / total_lines if total_lines > 0 else 0.0
                
                file_coverage_dict[file_path] = (covered_lines, missed_lines, percentage)
                
            return file_coverage_dict
            
        except Exception as e:
            self.logger.error(f"Error parsing diff coverage report: {e}")
            return {}

    def _file_matches(self, report_path: str, source_path: str) -> bool:
        """Check if a file path from the report matches our source file."""
        # Normalize paths for comparison
        report_path = os.path.normpath(report_path)
        source_path = os.path.normpath(source_path)
        
        # Check exact match
        if report_path == source_path:
            return True
            
        # Check if source path ends with report path (relative vs absolute)
        if source_path.endswith(report_path):
            return True
            
        # Check if report path ends with source path
        if report_path.endswith(os.path.basename(source_path)):
            return True
            
        return False

    def get_coverage(self) -> Optional[float]:
        """
        Legacy method for compatibility.
        Return coverage percent for the source file, or None if not found.
        """
        try:
            lines_covered, lines_missed, percentage = self._parse_single_file_coverage()
            return percentage * 100  # Convert to percentage
        except Exception as e:
            self.logger.error(f"Error getting coverage: {e}")
            return None
