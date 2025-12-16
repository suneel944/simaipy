# simaipy - AI/ML QA Automation Framework

A comprehensive test automation framework for validating AI-powered chatbots. This framework uses Playwright for UI automation and semantic similarity evaluation for AI response validation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Data](#test-data)
- [Test Reports](#test-reports)
- [Test Scenarios](#test-scenarios)

## Overview

This framework validates:

- **Chatbot UI Behavior**: Widget loading, message sending, response rendering, multilingual support
- **GPT-Powered Response Validation**: Semantic similarity checks, hallucination detection, consistency validation
- **Security & Injection Handling**: XSS protection, prompt injection defense

## Features

- **End-to-End UI Testing** using Playwright
- **Semantic Response Validation** using sentence transformers
- **Multilingual Support** (English & Arabic)
- **Security Testing** (XSS, prompt injection)
- **Interactive HTML Reports** with diff highlighting
- **Cross-Browser Testing** support
- **Parallel Test Execution**

## Project Structure

```
simaipy/
├── simaipy/                    # Core package
│   ├── report_generator.py    # HTML test report generator
│   ├── semantic_eval.py        # Semantic similarity evaluation
│   ├── config_loader.py       # Configuration management
│   └── config_model.py        # Configuration models
├── tests/                      # Test suite
│   ├── test_chat.py           # Main test cases
│   ├── test_data/
│   │   └── data.json         # Test cases (EN & AR)
│   └── pages/                 # Page Object Model
│       ├── chat_page.py
│       └── login_page.py
├── configs/                    # Environment configurations
│   ├── dev.yaml
│   ├── stage.yaml
│   └── prod.yaml
└── test-reports/              # Generated HTML reports
```

## Prerequisites

- Python 3.11+
- Node.js (for Playwright browsers)
- Access to chatbot application (credentials required)

## Installation

1. **Clone the repository** (if applicable)

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   pip install -e ".[dev]"
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

5. **Set up environment variables:**
   Create a `.env` file:
   ```bash
   SIMAI_ENV=dev
   SIMAI_BASE_URL=https://example.com
   SIMAI_USER_EMAIL=your-email@example.com
   SIMAI_USER_PASSWORD=your-password
   SIMAI_SEMANTIC_MODEL=sentence-transformers/all-MiniLM-L6-v2
   SIMAI_SEMANTIC_POS_THRESHOLD=0.7
   SIMAI_SEMANTIC_NEG_THRESHOLD=0.3
   SIMAI_TIMEOUT_SECONDS=30
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SIMAI_ENV` | Environment name (dev/stage/prod) | Yes |
| `SIMAI_BASE_URL` | Base URL of the application | Yes |
| `SIMAI_USER_EMAIL` | Login email for the application | Yes |
| `SIMAI_USER_PASSWORD` | Login password for the application | Yes |
| `SIMAI_SEMANTIC_MODEL` | HuggingFace model for semantic evaluation | Yes |
| `SIMAI_SEMANTIC_POS_THRESHOLD` | Positive similarity threshold (0.0-1.0) | Yes |
| `SIMAI_SEMANTIC_NEG_THRESHOLD` | Negative similarity threshold (0.0-1.0) | Yes |
| `SIMAI_TIMEOUT_SECONDS` | Request timeout in seconds | Yes |

### Configuration Files

Configuration can also be provided via YAML files in `configs/` directory:

```yaml
env: dev
base_url: https://example.com
timeout_seconds: 30
semantic_pos_threshold: 0.7
semantic_neg_threshold: 0.3
user_email: your-email@example.com
user_password: your-password
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
make test

# Run tests in parallel
make test-parallel

# Run specific test markers
pytest -m ui              # UI tests only
pytest -m semantic        # Semantic validation tests only
```

### Cross-Browser Testing

```bash
# Test across all browsers
make test-cross-browser

# Parallel cross-browser testing
make test-parallel-cross-browser
```

### View Test Reports

After running tests, HTML reports are automatically generated in `test-reports/` directory. Open the latest report in your browser:

```bash
# Reports are saved as: test-reports/test_report_YYYYMMDD_HHMMSS.html
```

## Test Data

Test cases are defined in `tests/test_data/data.json`. Each test case includes:

- `id`: Unique test identifier
- `locale`: Language (en/ar/both)
- `category`: Test category (ui/security/semantic_consistency)
- `prompt`: User input/question
- `expected_response`: Expected detailed response text
- `expectation`: Semantic expectation description
- `negative_expectation`: What the response should NOT contain
- `type`: Test type (public_service_query/prompt_injection/xss/consistency_check)

### Example Test Case

```json
{
  "id": "ui-en-basic",
  "locale": "en",
  "category": "ui",
  "prompt": "How can I renew my Emirates ID?",
  "expected_response": "## Step-by-Step Guide: Renewing Your Emirates ID...",
  "expectation": "The chatbot should respond with clear, step-by-step guidance...",
  "negative_expectation": "The reply must not be off-topic, fabricated...",
  "type": "public_service_query"
}
```

## Test Reports

The framework generates comprehensive HTML reports with:

- **Dashboard View**: Summary statistics (Total, Passed, Failed, Pass Rate)
- **Interactive Test Cards**: Expandable test cases with detailed information
- **Side-by-Side Comparison**: Actual vs Expected responses with diff highlighting
- **Search & Filter**: Filter by status (All/Passed/Failed)
- **Similarity Scores**: Semantic similarity metrics for each test

### Report Features

- Visual diff highlighting (insertions, deletions, replacements)
- Copy-to-clipboard functionality for prompts
- Responsive design for mobile viewing
- Detailed similarity scores and metadata

## Test Scenarios

### A. Chatbot UI Behavior

- Chat widget loads correctly
- User can send messages via input box
- AI responses are rendered properly
- Multilingual support (English & Arabic)
- Input clearing after sending (implicitly tested)
- Scroll and accessibility (can be enhanced)

### B. GPT-Powered Response Validation

- AI provides clear and helpful responses
- Responses are not hallucinated (via negative expectations)
- Responses stay consistent (consistency check test case)
- Response formatting validation (via semantic evaluation)
- Loading states (can be enhanced)

### C. Security & Injection Handling

- Chat input sanitization (XSS test case)
- Prompt injection defense (prompt injection test case)

## Test Categories

### UI Tests (`@pytest.mark.ui`)

Tests that validate the user interface behavior and semantic response quality:

```bash
pytest -m ui
```

### Semantic Tests (`@pytest.mark.semantic`)

Tests that validate AI response quality and security:

```bash
pytest -m semantic
```

## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run all checks
make check
```

### Adding New Test Cases

1. Add test case to `tests/test_data/data.json`
2. Include:
   - Unique `id`
   - Appropriate `category` and `type`
   - `prompt` in target language
   - `expected_response` with detailed expected answer
   - `expectation` for semantic validation
   - `negative_expectation` to prevent hallucinations

## Notes

- **Semantic Model**: The framework uses HuggingFace sentence transformers for semantic evaluation. Choose a model that supports your target languages (e.g., `paraphrase-multilingual-MiniLM-L12-v2` for Arabic support).

- **Thresholds**: Adjust `semantic_pos_threshold` and `semantic_neg_threshold` based on your requirements:
  - Higher `pos_threshold` = stricter matching
  - Lower `neg_threshold` = stricter negative matching

- **Mobile Testing**: While the framework supports cross-browser testing, explicit mobile viewport testing can be added by configuring Playwright viewport sizes.

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Run `make check` before committing

## License

MIT License

## Acknowledgments

Built for testing AI-powered chatbots and conversational interfaces.

