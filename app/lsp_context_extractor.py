import os
from lsp.ContextHelper import ContextHelper
from lsp.file_map.file_map import FileMap

class LSPContextExtractor:
    """
    Uses the LSP to extract context for a given source/test file.
    """
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.context_helper = ContextHelper(project_root)

    def get_context(self, file_path: str):
        """Return context (e.g., functions, classes, etc.) for the file."""
        fname_summary = FileMap(
            file_path,
            parent_context=True,
            child_context=True,
            header_max=10,
            project_base_path=self.project_root,
        )
        query_results, captures = fname_summary.get_query_results()
        return query_results, captures
