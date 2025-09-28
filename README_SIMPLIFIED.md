# Simplified Cover Agent

A streamlined version of the qodo-ai cover agent, designed specifically for Python and JavaScript projects with Ollama-based LLM support only.

## 🎯 Key Features

- **Python & JavaScript Only**: Focused support for the two most common languages
- **Ollama-Only LLM Support**: No OpenAI API costs - uses local open-source models
- **PostgreSQL Database**: Stores test generation results and metrics
- **Simplified Architecture**: Easier to understand and modify
- **No Complex Reports**: Focus on test generation, not reporting

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+** with pip
2. **Ollama** installed and running
3. **PostgreSQL** database (optional, will gracefully degrade)

### 1. Install Ollama

```bash
# Windows (using scoop)
scoop install ollama

# Start Ollama server
ollama serve

# Pull a code generation model
ollama pull deepseek-coder
```

### 2. Set up the Project

```bash
# Clone or download the project
cd Unit_Test_Generator

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac

# Install dependencies (already done for you)
pip install -r requirements.txt
```

### 3. Set up Database (Optional)

Create a `.env` file in the project root:

```env
DB_HOSTNAME=localhost
DB_PORT=5432
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_NAME=cover_agent_db
```

### 4. Test the Setup

```bash
# Test basic functionality
python minimal_demo.py
```

### 5. Generate Tests

```bash
# Example for Python project
python app/main_new.py \
  --source-file-path src/calculator.py \
  --test-file-path tests/test_calculator.py \
  --test-command "pytest tests/test_calculator.py --cov=src --cov-report=xml" \
  --model deepseek-coder \
  --desired-coverage 80

# Example for JavaScript project
python app/main_new.py \
  --source-file-path src/utils.js \
  --test-file-path tests/utils.test.js \
  --test-command "npm test -- --coverage" \
  --model deepseek-coder \
  --desired-coverage 75
```

## 📁 Project Structure

```
Unit_Test_Generator/
├── app/
│   ├── ai_caller.py           # Ollama API interface
│   ├── cover_agent.py         # Main orchestration class
│   ├── coverage_processor.py  # Coverage report parsing
│   ├── database.py           # PostgreSQL integration
│   ├── main_new.py           # CLI entry point
│   ├── prompt_builder.py     # AI prompt construction
│   ├── unit_test_generator.py # Test generation logic
│   └── unit_test_validator.py # Test validation logic
├── minimal_demo.py           # Simple functionality test
├── requirements.txt          # Python dependencies
└── README_SIMPLIFIED.md     # This file
```

## 🔧 Configuration

The system uses TOML configuration files in `app/config/`:

- `configuration.toml` - Main settings
- `test_generation_prompt.toml` - AI prompts for test generation
- Other prompt templates for various tasks

## 🎮 Usage Examples

### Python Project with pytest

```bash
python app/main_new.py \
  --source-file-path myproject/calculator.py \
  --test-file-path tests/test_calculator.py \
  --test-command "pytest tests/test_calculator.py --cov=myproject --cov-report=xml" \
  --desired-coverage 85 \
  --max-iterations 3
```

### JavaScript Project with Jest

```bash
python app/main_new.py \
  --source-file-path src/math-utils.js \
  --test-file-path __tests__/math-utils.test.js \
  --test-command "npm test -- --coverage --testPathPattern=math-utils" \
  --desired-coverage 80 \
  --max-iterations 5
```

## 🛠️ Available Models

Popular models that work well with this system:

- `deepseek-coder` (recommended)
- `codellama`
- `qwen2.5-coder`
- `codegemma`

Pull models with: `ollama pull <model-name>`

## 🔍 Command Line Options

```
--source-file-path      Path to source file to generate tests for
--test-file-path        Path to test file (created if doesn't exist)
--test-command          Command to run tests and generate coverage
--model                 Ollama model name (default: deepseek-coder)
--api-base              Ollama API URL (default: http://localhost:11434)
--desired-coverage      Target coverage percentage (default: 70)
--max-iterations        Maximum iterations to attempt (default: 3)
--max-run-time-sec      Max test execution time (default: 30)
--test-command-dir      Directory to run tests in
--project-root          Project root directory
--log-level             Logging level (DEBUG/INFO/WARNING/ERROR)
--verify-ollama         Verify Ollama connection before starting
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'ollama'"**: Make sure Ollama is installed and `ollama serve` is running
2. **"Model not found"**: Pull the model with `ollama pull deepseek-coder`
3. **Database connection errors**: Check your `.env` file or run without database
4. **Import errors**: Make sure you're in the virtual environment

### Getting Help

1. Check that Ollama is running: `curl http://localhost:11434/api/tags`
2. Test basic functionality: `python minimal_demo.py`
3. Check logs for detailed error messages
4. Ensure all dependencies are installed: `pip list`

## 🎯 Differences from Original qodo-cover

- **Simplified Language Support**: Only Python & JavaScript (vs 10+ languages)
- **Ollama-Only**: No OpenAI API costs or complexity
- **No HTML/XML Reports**: Focus on test generation
- **PostgreSQL**: Instead of SQLite for better scalability
- **Streamlined Architecture**: Easier to understand and modify

## 🤝 Contributing

This is a simplified, educational version of qodo-cover. Feel free to:

- Add support for more Ollama models
- Improve prompt templates
- Add more language-specific features
- Enhance error handling

## 📄 License

Based on qodo-ai/qodo-cover (AGPL-3.0). This simplified version maintains the same license.
