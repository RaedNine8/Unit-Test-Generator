import xml.etree.ElementTree as ET
import logging
from typing import Optional

class CoverageProcessor:
    """
    Parses a coverage XML report (pytest-cov/coverage.py) and returns coverage percentage for a given file.
    """
    def __init__(self, coverage_report_path: str, source_file_path: str):
        self.coverage_report_path = coverage_report_path
        self.source_file_path = source_file_path
        self.logger = logging.getLogger(__name__)

    def get_coverage(self) -> Optional[float]:
        """Return coverage percent for the source file, or None if not found."""
        try:
            tree = ET.parse(self.coverage_report_path)
            root = tree.getroot()
            # For coverage.py XML, look for <class filename="..."> or <file name="...">
            for file_elem in root.iter():
                filename = file_elem.attrib.get("filename") or file_elem.attrib.get("name")
                if filename and self.source_file_path in filename:
                    lines_covered = int(file_elem.attrib.get("covered", 0))
                    lines_missed = int(file_elem.attrib.get("missed", 0))
                    total = lines_covered + lines_missed
                    if total == 0:
                        return 0.0
                    return 100.0 * lines_covered / total
            return None
        except Exception as e:
            self.logger.error(f"Error parsing coverage report: {e}")
            return None
