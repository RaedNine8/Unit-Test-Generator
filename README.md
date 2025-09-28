# Simplified Cover Agent

A simplified version of the qodo-cover agent focused on Python and JavaScript test generation using Ollama (open-source LLMs only). This tool automatically generates unit tests to improve code coverage without the complexity of the original qodo-cover implementation.

## 🎯 Key Features

- **🚀 Simplified Architecture**: Streamlined version focused on core functionality
- **🤖 Ollama-Only LLM Support**: Uses local, open-source models via Ollama
- **🐍 Python & JavaScript Support**: Focused on the two most common languages
- **📊 Coverage-Driven**: Automatically improves test coverage iteratively
- **🗄️ PostgreSQL Logging**: Stores test generation results in PostgreSQL
- **❌ No HTML/XML Reports**: Simplified output without complex reporting

## 🏗️ Architecture

The simplified cover agent consists of these core components:

1. **CoverAgent**: Main orchestration class that coordinates the entire process
2. **AICaller**: Handles communication with Ollama LLMs
3. **PromptBuilder**: Constructs prompts for test generation
4. **UnitTestGenerator**: Generates new unit tests using AI
5. **UnitTestValidator**: Validates and runs generated tests
6. **CoverageProcessor**: Processes coverage reports (Cobertura, LCOV)
7. **Database**: PostgreSQL integration for logging results

## 📋 Prerequisites

- **Python 3.8+**
- **Ollama** running locally (with a coding model like `deepseek-coder`)
- **PostgreSQL** database
- **Coverage tools** for your language:
  - Python: `pytest-cov` or `coverage.py`
  - JavaScript: `jest`, `nyc`, or similar

## 🚀 Quick Start

### 1. Setup

```powershell
# Clone or download the project
cd Unit_Test_Generator

# Run the setup script
python setup.py
```

The setup script will:

- Check prerequisites
- Install dependencies
- Create configuration templates
- Set up example files

### 2. Configure Environment

Edit the `.env` file created by the setup script:

```env
# PostgreSQL Database Configuration
DB_HOSTNAME=localhost
DB_PORT=5432
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_NAME=cover_agent_db

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_FILE=cover_agent.log
```

### 3. Start Ollama and Pull a Model

```powershell
# Start Ollama service
ollama serve

# Pull a recommended coding model
ollama pull deepseek-coder
# or
ollama pull codellama
```

### 4. Run the Cover Agent

```powershell
# Basic usage
python cover-agent-cli.py `
  --source-file-path "src/calculator.py" `
  --test-file-path "tests/test_calculator.py" `
  --test-command "pytest tests/test_calculator.py --cov=src --cov-report=xml"

# With custom settings
python cover-agent-cli.py `
  --source-file-path "src/utils.js" `
  --test-file-path "tests/utils.test.js" `
  --test-command "npm test -- --coverage" `
  --model "deepseek-coder" `
  --desired-coverage 80 `
  --max-iterations 5
```

## 📖 Usage Examples

### Python Project

```powershell
python cover-agent-cli.py `
  --source-file-path "src/calculator.py" `
  --test-file-path "tests/test_calculator.py" `
  --test-command "pytest tests/test_calculator.py --cov=src --cov-report=xml --cov-report=term" `
  --desired-coverage 85 `
  --max-iterations 3
```

### JavaScript Project

```powershell
python cover-agent-cli.py `
  --source-file-path "src/utils.js" `
  --test-file-path "tests/utils.test.js" `
  --test-command "npm test -- --coverage --coverageReporters=cobertura" `
  --model "codellama" `
  --desired-coverage 75
```

## ⚙️ Command Line Options

| Option               | Description                 | Default                  |
| -------------------- | --------------------------- | ------------------------ |
| `--source-file-path` | Path to source file to test | **Required**             |
| `--test-file-path`   | Path to test file           | **Required**             |
| `--test-command`     | Command to run tests        | **Required**             |
| `--model`            | Ollama model name           | `deepseek-coder`         |
| `--api-base`         | Ollama API URL              | `http://localhost:11434` |
| `--desired-coverage` | Target coverage %           | `70`                     |
| `--max-iterations`   | Max iterations              | `3`                      |
| `--max-run-time-sec` | Max test execution time     | `30`                     |
| `--test-command-dir` | Test command directory      | Auto-detected            |
| `--project-root`     | Project root directory      | Auto-detected            |
| `--log-level`        | Logging level               | `INFO`                   |
| `--verify-ollama`    | Verify Ollama before start  | `False`                  |

## 📊 How It Works

1. **Initialize**: Validates files, connects to Ollama and database
2. **Baseline Coverage**: Runs existing tests to establish baseline coverage
3. **Iterative Generation**: For each iteration:
   - Analyzes coverage gaps
   - Generates new tests using AI
   - Validates generated tests
   - Updates coverage metrics
4. **Results**: Logs final results to database and console

## 🛠️ Configuration

### Models

Recommended Ollama models for code generation:

- **deepseek-coder**: Excellent for Python and JavaScript
- **codellama**: Good general-purpose coding model
- **llama3.1**: Newer model with good coding capabilities

### Coverage Tools

The agent supports these coverage report formats:

- **Cobertura XML**: Most common format (pytest-cov, jest)
- **LCOV**: Used by many JavaScript tools
- **JaCoCo**: Limited support (mainly for Java projects)

### Database Schema

The agent creates a simple table to track test runs:

```sql
CREATE TABLE test_runs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR(255),
    tests_generated INTEGER,
    tests_passed INTEGER
);
```

## 🔧 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**

   ```powershell
   # Start Ollama service
   ollama serve

   # Check if models are available
   ollama list
   ```

2. **PostgreSQL Connection Failed**

   - Verify database credentials in `.env`
   - Ensure PostgreSQL service is running
   - Create the database if it doesn't exist

3. **Coverage Report Not Found**

   - Ensure your test command generates coverage reports
   - Check the coverage file path and format
   - Verify test command runs successfully

4. **Python Import Errors**

   ```powershell
   # Install missing dependencies
   pip install -r requirements-simplified.txt

   # Or install individually
   pip install requests psycopg2-binary python-dotenv jinja2 pyyaml
   ```

### Debug Mode

Run with debug logging for detailed information:

```powershell
python cover-agent-cli.py `
  --log-level DEBUG `
  --log-file debug.log `
  --verify-ollama `
  [other options...]
```

## 🚧 Limitations

This simplified version has the following limitations compared to the original qodo-cover:

- **Languages**: Only Python and JavaScript/TypeScript
- **LLM Providers**: Only Ollama (no OpenAI, Anthropic, etc.)
- **Reports**: No HTML or XML report generation
- **CI/CD**: No built-in CI/CD integrations
- **Language Features**: Reduced language-specific optimizations

## 🤝 Contributing

This is a simplified implementation. To extend functionality:

1. **Add Language Support**: Extend `detect_language()` and add coverage processors
2. **Add LLM Providers**: Extend `AICaller` class
3. **Improve Prompts**: Modify TOML files in `app/config/`
4. **Add Features**: Extend the core classes

## 📄 License

This project is based on the qodo-cover agent and maintains the same AGPL-3.0 license.

## 🙏 Acknowledgments

- Original [qodo-cover](https://github.com/qodo-ai/qodo-cover) project
- [Ollama](https://ollama.ai/) for local LLM support
- The open-source AI community

---

**Happy Testing! 🧪✨**
