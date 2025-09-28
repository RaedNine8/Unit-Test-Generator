from typing import Optional, Tuple
import logging

from jinja2 import Environment, StrictUndefined

from app.abstract.prompt_builder_abc import PromptBuilderABC
from ai_caller import AICaller
from app.logging.custom_logger import CustomLogger
from config.config_loader import get_settings
from utility.utils import load_yaml


class PromptBuilder(PromptBuilderABC):
    """
    A default implementation of PromptBuilderABC that relies on TOML-based
    prompt templates for each method. It uses _build_prompt() to construct the
    prompt from the appropriate TOML file, then calls an AI model via AICaller
    to get the response.
    """

    def __init__(self, caller: AICaller, logger: Optional[CustomLogger] = None, generate_log_files: bool = True):
        """
        Initializes the PromptBuilder.

        Args:
            caller (AICaller): A class responsible for sending the prompt to an AI model and returning the response.
            logger (CustomLogger, optional): The logger object for logging messages.
            generate_log_files (bool, optional): Whether or not to generate logs.
        """
        self.caller = caller
        self.logger = logger or CustomLogger.get_logger(__name__, generate_log_files=generate_log_files)

    def _build_prompt(self, file: str, **kwargs) -> dict:
        """
        Internal helper that builds {"system": ..., "user": ...} for the model
        by loading Jinja2 templates from TOML-based settings.

        The `file` argument corresponds to the name/key in your TOML file,
        e.g. "analyze_test_against_context". All other variables are passed
        in via **kwargs. The TOML's system/user templates may reference these
        variables using Jinja2 syntax, e.g. {{ language }} or {{ test_file_content }}.

        Raises:
            ValueError: If the TOML config does not contain valid 'system' and 'user' keys.
            RuntimeError: If an error occurs while rendering the templates.
        """
        environment = Environment(undefined=StrictUndefined)

        try:
            # 1. Fetch the prompt config from your TOML-based settings
            prompt_config = getattr(get_settings(), file, None)
            if not prompt_config:
                raise ValueError(f"Prompt configuration '{file}' not found in settings")

            # 2. Get the system and user templates
            system_template = getattr(prompt_config, 'system', '')
            user_template = getattr(prompt_config, 'user', '')

            if not system_template and not user_template:
                raise ValueError(f"Neither 'system' nor 'user' templates found in config '{file}'")

            # 3. Render the templates with the provided variables
            system_prompt = environment.from_string(system_template).render(**kwargs) if system_template else ""
            user_prompt = environment.from_string(user_template).render(**kwargs) if user_template else ""

            return {"system": system_prompt, "user": user_prompt}

        except Exception as e:
            error_msg = f"Error building prompt from template '{file}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def generate_tests(
        self,
        source_file_name: str,
        max_tests: int,
        source_file_numbered: str,
        code_coverage_report: str,
        language: str,
        test_file: str,
        test_file_name: str,
        testing_framework: str,
        additional_instructions_text: str = None,
        additional_includes_section: str = None,
        failed_tests_section: str = None,
    ) -> Tuple[str, int, int, str]:
        """
        Generates additional unit tests using the 'test_generation_prompt.toml' template.

        Args:
            source_file_name (str): Name/path of the source file being tested.
            max_tests (int): Maximum number of tests to generate.
            source_file_numbered (str): Source code with line numbers.
            code_coverage_report (str): Coverage data highlighting untested lines or blocks.
            language (str): Programming language of the source code and tests (e.g., "python").
            test_file (str): The existing test file content.
            test_file_name (str): Name/path of the existing test file.
            testing_framework (str): The testing framework in use (e.g., "pytest", "unittest").
            additional_instructions_text (str, optional): Extra instructions or context for the AI.
            additional_includes_section (str, optional): Additional code or includes.
            failed_tests_section (str, optional): Details of failed tests to consider.

        Returns:
            Tuple[str, int, int, str]:
                A 4-element tuple containing:
                - The AI-generated test suggestions (string),
                - The input token count (int),
                - The output token count (int),
                - The final constructed prompt sent to the AI (str).
        """
        prompt = self._build_prompt(
            file="test_generation_prompt",
            source_file_name=source_file_name,
            max_tests=max_tests,
            source_file_numbered=source_file_numbered,
            code_coverage_report=code_coverage_report,
            language=language,
            test_file=test_file,
            test_file_name=test_file_name,
            testing_framework=testing_framework,
            additional_instructions_text=additional_instructions_text or "",
            additional_includes_section=additional_includes_section or "",
            failed_tests_section=failed_tests_section or "",
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)

    def analyze_test_failure(
        self,
        source_file_name: str,
        source_file: str,
        processed_test_file: str,
        stdout: str,
        stderr: str,
        test_file_name: str,
    ) -> Tuple[str, int, int, str]:
        """
        Analyzes a test run failure using the 'analyze_test_run_failure.toml' template.

        Args:
            source_file_name (str): Name/path of the source file.
            source_file (str): The source file content.
            processed_test_file (str): The processed test file content.
            stdout (str): Standard output from the test run.
            stderr (str): Standard error from the test run.
            test_file_name (str): Name/path of the test file.

        Returns:
            Tuple[str, int, int, str]: AI response, input tokens, output tokens, prompt.
        """
        prompt = self._build_prompt(
            file="analyze_test_run_failure",
            source_file_name=source_file_name, 
            source_file=source_file,
            processed_test_file=processed_test_file,
            stdout=stdout,
            stderr=stderr,
            test_file_name=test_file_name,
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)

    def analyze_test_insert_line(
        self,
        language: str,
        test_file_numbered: str,
        test_file_name: str,
        additional_instructions_text: str = None,
    ) -> Tuple[str, int, int, str]:
        """
        Determines the correct line number(s) to insert new test cases, using
        'analyze_suite_test_insert_line.toml'.

        Args:
            language (str): Programming language.
            test_file_numbered (str): Test file content with line numbers.
            test_file_name (str): Name/path of the test file.
            additional_instructions_text (str, optional): Additional instructions.

        Returns:
            Tuple[str, int, int, str]: AI response, input tokens, output tokens, prompt.
        """
        prompt = self._build_prompt(
            file="analyze_suite_test_insert_line",
            language=language,
            test_file_numbered=test_file_numbered,
            test_file_name=test_file_name,
            additional_instructions_text=additional_instructions_text or "",
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)

    def analyze_test_against_context(
        self,
        language: str,
        test_file_content: str,
        test_file_name_rel: str,
        context_files_names_rel: str,
    ) -> Tuple[str, int, int, str]:
        """
        Examines a test file against context files using 'analyze_test_against_context.toml'.

        Args:
            language (str): Programming language.
            test_file_content (str): Content of the test file.
            test_file_name_rel (str): Relative path to the test file.
            context_files_names_rel (str): Context files information.

        Returns:
            Tuple[str, int, int, str]: AI response, input tokens, output tokens, prompt.
        """
        prompt = self._build_prompt(
            file="analyze_test_against_context",
            language=language,
            test_file_content=test_file_content,
            test_file_name_rel=test_file_name_rel,
            context_files_names_rel=context_files_names_rel,
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)

    def analyze_suite_test_headers_indentation(
        self,
        language: str,
        test_file_name: str,
        test_file: str,
    ) -> Tuple[str, int, int, str]:
        """
        Inspects a test suite's header indentation using 'analyze_suite_test_headers_indentation.toml'.

        Args:
            language (str): Programming language.
            test_file_name (str): Name/path of the test file.
            test_file (str): Content of the test file.

        Returns:
            Tuple[str, int, int, str]: AI response, input tokens, output tokens, prompt.
        """
        prompt = self._build_prompt(
            file="analyze_suite_test_headers_indentation",
            language=language,
            test_file_name=test_file_name,
            test_file=test_file,
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)

    def adapt_test_command_for_a_single_test_via_ai(
        self,
        test_file_relative_path: str,
        test_command: str,
        project_root_dir: str,
    ) -> Tuple[str, int, int, str]:
        """
        Adapts a project-wide test command to run a single test file, using
        'adapt_test_command_for_a_single_test_via_ai.toml'.

        Args:
            test_file_relative_path (str): Relative path to the test file.
            test_command (str): The original test command.
            project_root_dir (str): Project root directory.

        Returns:
            Tuple[str, int, int, str]: AI response, input tokens, output tokens, prompt.
        """
        prompt = self._build_prompt(
            file="adapt_test_command_for_a_single_test_via_ai",
            test_file_relative_path=test_file_relative_path,
            test_command=test_command,
            project_root_dir=project_root_dir,
        )
        
        response, prompt_tokens, completion_tokens = self.caller.call(prompt)
        return response, prompt_tokens, completion_tokens, str(prompt)
