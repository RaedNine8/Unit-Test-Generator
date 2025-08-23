from pathlib import Path
from typing import Dict

class PromptBuilder:
    """
    Builds prompts for the LLM using source and test file content.
    """
    def __init__(self, source_file_path: str, test_file_path: str):
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path

    def build_prompt(self) -> Dict[str, str]:
        """Return a dict with 'system' and 'user' keys for the LLM."""
        with open(self.source_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            test_code = f.read()
        system = "You are an expert test generator."
        user = f"Source code:\n{source_code}\n\nCurrent tests:\n{test_code}\n\nWrite more tests to increase coverage."
        return {"system": system, "user": user}
