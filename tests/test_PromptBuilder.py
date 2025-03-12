import pytest
from llm_handler.PromptBuilder import PromptBuilder
import os
import tempfile

class TestPromptBuilder:
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create source file
            source_path = os.path.join(tmpdirname, "source.py")
            with open(source_path, "w") as f:
                f.write("def add(a, b):\n    return a + b")

            # Create test file
            test_path = os.path.join(tmpdirname, "test_source.py")
            with open(test_path, "w") as f:
                f.write("def test_add():\n    assert add(1, 2) == 3")

            # Create coverage report
            coverage_path = os.path.join(tmpdirname, "coverage.xml")
            with open(coverage_path, "w") as f:
                f.write("<coverage>test coverage data</coverage>")

            yield {
                "source_path": source_path,
                "test_path": test_path,
                "coverage_path": coverage_path,
                "project_root": tmpdirname
            }

    @pytest.fixture
    def prompt_builder(self, temp_files):
        """Create PromptBuilder instance"""
        return PromptBuilder(
            source_file_path=temp_files["source_path"],
            test_file_path=temp_files["test_path"],
            code_coverage_report="Test Coverage: 80%",
            project_root=temp_files["project_root"]
        )

    def test_initialization(self, prompt_builder):
        """Test proper initialization of PromptBuilder"""
        assert prompt_builder.language == "python"
        assert prompt_builder.testing_framework == "NOT KNOWN"
        assert prompt_builder.source_file.strip() == "def add(a, b):\n    return a + b"
        assert prompt_builder.test_file.strip() == "def test_add():\n    assert add(1, 2) == 3"

    def test_file_numbering(self, prompt_builder):
        """Test line numbering functionality"""
        numbered_lines = prompt_builder.source_file_numbered.split('\n')
        assert numbered_lines[0].startswith("1 def")
        assert numbered_lines[1].startswith("2     return")

    def test_build_prompt_basic(self, prompt_builder):
        """Test basic prompt building"""
        prompt = prompt_builder.build_prompt()
        assert isinstance(prompt, dict)
        assert "system" in prompt
        assert "user" in prompt

    def test_build_prompt_with_additional_content(self, temp_files):
        """Test prompt building with additional content"""
        builder = PromptBuilder(
            source_file_path=temp_files["source_path"],
            test_file_path=temp_files["test_path"],
            code_coverage_report="Test Coverage: 80%",
            included_files="additional.py",
            additional_instructions="Test edge cases",
            failed_test_runs="Previous failure log",
            project_root=temp_files["project_root"]
        )
        prompt = builder.build_prompt()
        assert "additional.py" in builder.included_files
        assert "Test edge cases" in builder.additional_instructions
        assert "Previous failure log" in builder.failed_test_runs

    def test_build_prompt_custom(self, prompt_builder):
        """Test custom prompt building"""
        custom_prompt = prompt_builder.build_prompt_custom("test_generation_prompt")
        assert isinstance(custom_prompt, dict)
        assert "system" in custom_prompt
        assert "user" in custom_prompt

    def test_file_reading_error(self):
        """Test handling of non-existent files"""
        test_dir = tempfile.gettempdir()
        nonexistent_source = os.path.join(test_dir, "nonexistent.py")
        nonexistent_test = os.path.join(test_dir, "nonexistent_test.py")
        
        # Create empty coverage report to focus on source/test files
        coverage_path = os.path.join(test_dir, "coverage.xml")
        with open(coverage_path, "w") as f:
            f.write("")
        
        try:
            PromptBuilder(
                source_file_path=nonexistent_source,
                test_file_path=nonexistent_test,
                code_coverage_report=coverage_path,
                project_root=test_dir
            )
            pytest.fail("Expected FileNotFoundError was not raised")
        except Exception as e:
            assert isinstance(e, (FileNotFoundError, IOError))
            assert any(path in str(e) for path in [nonexistent_source, nonexistent_test])

    def test_relative_paths(self, temp_files):
        """Test relative path handling"""
        builder = PromptBuilder(
            source_file_path=temp_files["source_path"],
            test_file_path=temp_files["test_path"],
            code_coverage_report="coverage.xml",
            project_root=temp_files["project_root"]
        )
        assert os.path.basename(builder.source_file_name_rel) == "source.py"
        assert os.path.basename(builder.test_file_name_rel) == "test_source.py"

    def test_empty_optional_parameters(self, temp_files):
        """Test initialization with empty optional parameters"""
        builder = PromptBuilder(
            source_file_path=temp_files["source_path"],
            test_file_path=temp_files["test_path"],
            code_coverage_report="coverage.xml",
            project_root=temp_files["project_root"]
        )
        assert builder.included_files == ""
        assert builder.additional_instructions == ""
        assert builder.failed_test_runs == ""

    def test_stdout_stderr_handling(self, prompt_builder):
        """Test stdout and stderr handling"""
        prompt_builder.stdout_from_run = "Test output"
        prompt_builder.stderr_from_run = "Test error"
        prompt = prompt_builder.build_prompt()
        assert isinstance(prompt, dict)
        assert prompt_builder.stdout_from_run == "Test output"
        assert prompt_builder.stderr_from_run == "Test error"