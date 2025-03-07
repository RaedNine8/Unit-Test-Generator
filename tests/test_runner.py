import pytest
import os
from config.Runner import Runner
from time import sleep

class TestRunner:
    @pytest.fixture
    def runner(self):
        return Runner()

    def test_basic_command_execution(self, runner):
        """Test basic echo command execution"""
        stdout, stderr, exit_code, start_time = runner.run_command("echo Hello")
        assert stdout.strip() == "Hello"
        assert exit_code == 0
        assert stderr == ""
        assert isinstance(start_time, int)

    def test_command_timeout(self, runner):
        """Test command timeout handling"""
        # Command that sleeps for longer than timeout
        stdout, stderr, exit_code, start_time = runner.run_command("python -c \"import time; time.sleep(31)\"")
        assert exit_code == -1
        assert stderr == "Command timed out"
        assert stdout == ""

    def test_working_directory(self, runner, tmp_path):
        """Test command execution in specific working directory"""
        # Create temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # List directory contents
        stdout, stderr, exit_code, _ = runner.run_command("dir", cwd=str(tmp_path))
        assert exit_code == 0
        assert "test.txt" in stdout

    def test_invalid_command(self, runner):
        """Test handling of invalid commands"""
        stdout, stderr, exit_code, _ = runner.run_command("invalidcommand123")
        assert exit_code != 0
        assert stderr != ""

    def test_command_with_output(self, runner):
        """Test command that produces both stdout and stderr"""
        command = 'python -c "import sys; print(\'stdout\'); print(\'stderr\', file=sys.stderr)"'
        stdout, stderr, exit_code, _ = runner.run_command(command)
        assert stdout.strip() == "stdout"
        assert stderr.strip() == "stderr"
        assert exit_code == 0