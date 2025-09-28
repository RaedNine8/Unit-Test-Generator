# Simple working cover agent that just demonstrates the core functionality
import os
import logging
from typing import Optional

from app.logging.custom_logger import CustomLogger


class CoverAgent:
    """Simplified cover agent for generating unit tests to improve coverage."""
    
    def __init__(
        self,
        source_file_path: str,
        test_file_path: str,
        code_coverage_report_path: str,
        test_command: str,
        model: str = "deepseek-coder",
        api_base: str = "http://localhost:11434",
        desired_coverage: int = 70,
        max_iterations: int = 3,
        max_run_time_sec: int = 30,
        test_command_dir: Optional[str] = None,
        project_root: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        generate_log_files: bool = True,
    ):
        """Initialize the CoverAgent with simplified parameters."""
        self.source_file_path = source_file_path
        self.test_file_path = test_file_path
        self.code_coverage_report_path = code_coverage_report_path
        self.test_command = test_command
        self.model = model
        self.api_base = api_base
        self.desired_coverage = desired_coverage
        self.max_iterations = max_iterations
        self.max_run_time_sec = max_run_time_sec
        self.test_command_dir = test_command_dir or os.path.dirname(test_file_path)
        self.project_root = project_root or os.getcwd()
        
        # Initialize logger (returns standard logging.Logger)
        self.logger = logger or CustomLogger.get_logger(__name__, generate_log_files=generate_log_files)
        
        # State tracking
        self.current_coverage = 0.0
        self.iteration_count = 0
        self.tests_generated = 0
        self.tests_passed = 0

    def run(self, demo_mode: bool = None) -> bool:
        """
        Run the cover agent to generate tests and improve coverage.
        
        Args:
            demo_mode: If True, run in demo mode. If None, auto-detect based on Ollama availability.
        
        Returns:
            bool: True if target coverage was achieved, False otherwise
        """
        self.logger.info("=" * 60)
        self.logger.info("STARTING SIMPLIFIED COVER AGENT")
        self.logger.info("=" * 60)
        self.logger.info(f"Source file: {self.source_file_path}")
        self.logger.info(f"Test file: {self.test_file_path}")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Target coverage: {self.desired_coverage}%")
        
        # Auto-detect demo mode if not specified
        if demo_mode is None:
            demo_mode = not self._check_ollama_availability()
        
        if demo_mode:
            return self._run_demo_mode()
        else:
            return self._run_production_mode()
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and responsive."""
        try:
            import requests
            response = requests.get(f"{self.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _run_demo_mode(self) -> bool:
        """Run in demonstration mode with simulated results."""
        try:
            self.logger.info("🎭 RUNNING IN DEMONSTRATION MODE")
            self.logger.info("Full test generation requires:")
            self.logger.info("1. Working Ollama setup: ollama serve")
            self.logger.info("2. Pull a model: ollama pull deepseek-coder")
            self.logger.info("3. Re-run with --production flag")
            
            # Simulate some progress
            self.current_coverage = 0.45  # 45%
            self.tests_generated = 3
            self.tests_passed = 2
            self.iteration_count = 1
            
            self._print_summary()
            return False  # Return False since this is just a demo
            
        except Exception as e:
            self.logger.error(f"Error in demo mode: {e}", exc_info=True)
            return False
    
    def _run_production_mode(self) -> bool:
        """Run in production mode with real AI integration."""
        try:
            self.logger.info("🚀 RUNNING IN PRODUCTION MODE")
            
            # Initialize AI components
            if not self._initialize_ai_components():
                self.logger.error("Failed to initialize AI components")
                return False
            
            # Get baseline coverage
            self.logger.info("📊 Analyzing baseline coverage...")
            self.current_coverage = self._get_baseline_coverage()
            
            if self.current_coverage is None:
                self.logger.warning("Could not determine baseline coverage, starting from 0%")
                self.current_coverage = 0.0
            
            baseline_percent = self.current_coverage * 100
            self.logger.info(f"📈 Baseline coverage: {baseline_percent:.2f}%")
            
            # Check if target already achieved
            if baseline_percent >= self.desired_coverage:
                self.logger.info(f"✅ Target coverage {self.desired_coverage}% already achieved!")
                self._print_summary()
                return True
            
            # Run iterative test generation
            return self._run_generation_loop()
            
        except Exception as e:
            self.logger.error(f"Error in production mode: {e}", exc_info=True)
            return False
    
    def _initialize_ai_components(self) -> bool:
        """Initialize AI caller and related components."""
        try:
            from app.ai_caller import AICaller
            from app.prompt_builder import PromptBuilder
            from app.unit_test_generator import UnitTestGenerator
            from app.unit_test_validator import UnitTestValidator
            
            # Check if Ollama is available first
            ollama_available = self._check_ollama_availability()
            
            # Initialize AI caller (with simulation if Ollama not available)
            self.ai_caller = AICaller(
                model=self.model, 
                api_base=self.api_base,
                simulation_mode=not ollama_available
            )
            
            # Test AI connection
            if not self.ai_caller.test_connection():
                self.logger.error("Failed to initialize AI caller")
                return False
                
            if not ollama_available:
                self.logger.info("🎭 Using AI simulation mode (Ollama not available)")
            
            # Initialize prompt builder
            self.prompt_builder = PromptBuilder(caller=self.ai_caller)
            
            # Initialize test generator
            self.test_generator = UnitTestGenerator(
                source_file_path=self.source_file_path,
                test_file_path=self.test_file_path,
                code_coverage_report_path=self.code_coverage_report_path,
                test_command=self.test_command,
                llm_model=self.model,
                agent_completion=self.prompt_builder,
                test_command_dir=self.test_command_dir,
                project_root=self.project_root,
                logger=self.logger
            )
            
            # Initialize test validator
            self.test_validator = UnitTestValidator(
                source_file_path=self.source_file_path,
                test_file_path=self.test_file_path,
                code_coverage_report_path=self.code_coverage_report_path,
                test_command=self.test_command,
                llm_model=self.model,
                max_run_time_sec=self.max_run_time_sec,
                agent_completion=self.prompt_builder,
                desired_coverage=self.desired_coverage,
                test_command_dir=self.test_command_dir,
                project_root=self.project_root,
                logger=self.logger
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing AI components: {e}")
            return False
    
    def _get_baseline_coverage(self) -> Optional[float]:
        """Get the baseline coverage by running existing tests."""
        try:
            if hasattr(self, 'test_validator'):
                return self.test_validator.get_coverage()
            else:
                # Fallback: run test command and try to parse coverage
                import subprocess
                result = subprocess.run(
                    self.test_command.split(),
                    cwd=self.test_command_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.max_run_time_sec
                )
                
                if result.returncode == 0:
                    # Try to extract coverage from output (basic parsing)
                    output = result.stdout + result.stderr
                    # This is a simple heuristic - should be improved for production
                    import re
                    coverage_match = re.search(r'(\d+)%', output)
                    if coverage_match:
                        return float(coverage_match.group(1)) / 100.0
                
                return 0.0
                
        except Exception as e:
            self.logger.warning(f"Error getting baseline coverage: {e}")
            return None
    
    def _run_generation_loop(self) -> bool:
        """Run the iterative test generation loop."""
        self.logger.info(f"🔄 Starting generation loop (max {self.max_iterations} iterations)")
        
        for iteration in range(1, self.max_iterations + 1):
            self.iteration_count = iteration
            self.logger.info(f"\n--- ITERATION {iteration}/{self.max_iterations} ---")
            
            # Generate new tests
            self.logger.info("🧠 Generating new tests with AI...")
            test_results = self.test_generator.generate_tests()
            
            if not test_results or not test_results.get('new_tests', []):
                self.logger.warning("No tests were generated this iteration")
                continue
            
            generated_tests = test_results.get('new_tests', [])
            self.tests_generated += len(generated_tests)
            self.logger.info(f"📝 Generated {len(generated_tests)} new tests")
            
            # Validate generated tests
            self.logger.info("✅ Validating generated tests...")
            passed_count = 0
            
            for test_data in generated_tests:
                validation_result = self.test_validator.validate_test(test_data)
                if validation_result and validation_result.get('status') == 'PASS':
                    passed_count += 1
                    self.tests_passed += 1
            
            self.logger.info(f"✔️ {passed_count}/{len(generated_tests)} tests passed validation")
            
            # Update coverage
            new_coverage = self._get_baseline_coverage()
            if new_coverage is not None and new_coverage > self.current_coverage:
                improvement = (new_coverage - self.current_coverage) * 100
                self.current_coverage = new_coverage
                self.logger.info(f"📈 Coverage improved by {improvement:.2f}% to {new_coverage * 100:.2f}%")
                
                # Check if target achieved
                if new_coverage * 100 >= self.desired_coverage:
                    self.logger.info(f"🎯 Target coverage {self.desired_coverage}% achieved!")
                    self._print_summary()
                    return True
            else:
                self.logger.warning("No coverage improvement this iteration")
        
        # Completed all iterations
        final_coverage = (self.current_coverage * 100) if self.current_coverage else 0.0
        success = final_coverage >= self.desired_coverage
        
        self.logger.info(f"🏁 Completed {self.max_iterations} iterations")
        self._print_summary()
        
        return success
    
    def _print_summary(self):
        """Print a summary of the test generation results."""
        final_coverage_percent = self.current_coverage * 100 if self.current_coverage else 0.0
        success = final_coverage_percent >= self.desired_coverage
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("TEST GENERATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Final coverage: {final_coverage_percent:.2f}%")
        self.logger.info(f"Target coverage: {self.desired_coverage}%")
        self.logger.info(f"Tests generated: {self.tests_generated}")
        self.logger.info(f"Tests passed: {self.tests_passed}")
        self.logger.info(f"Iterations completed: {self.iteration_count}")
        self.logger.info(f"Success: {'✅ YES' if success else '❌ NO'}")
