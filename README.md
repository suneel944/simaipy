# simaipy - AI/ML QA Automation Framework

A test automation framework for validating AI-powered chatbots using Playwright for UI automation and semantic similarity evaluation for response validation.

## Features

- **End-to-End UI Testing** with Playwright
- **Semantic Response Validation** using sentence transformers
- **Multilingual Support** (English & Arabic)
- **Security Testing** (XSS, prompt injection)
- **Interactive HTML Reports** with diff highlighting
- **Cross-Browser & Parallel Execution**

## Quick Start

### Installation

```bash
# Check dependencies and set up project
make check-dependencies
make setup

# Install Playwright browsers
make install-playwright BROWSER=chromium

# Optional: Install pytest-xdist for parallel execution
.venv/bin/pip install pytest-xdist
```

### Configuration

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

Or use YAML files in `configs/` directory (see `configs/dev.yaml` for format).

### Running Tests

```bash
# Run all tests (generates HTML report automatically)
make test

# Run tests in parallel
make test-parallel

# Run specific test markers
.venv/bin/pytest -m ui        # UI tests
.venv/bin/pytest -m semantic  # Semantic validation
.venv/bin/pytest -m security  # Security tests

# Cross-browser testing
make test-cross-browser
make test-parallel-cross-browser
```

**Note:** Parallel execution requires `pytest-xdist`: `pip install pytest-xdist`

## Test Data

Test cases are defined in `tests/test_data/data.json`. Each test case includes:

- `id`, `locale`, `category`, `type`
- `prompt`: User input/question
- `expected_response`: Expected response text
- `expectation`: Semantic expectation description
- `negative_expectation`: What the response should NOT contain

### Example

```json
{
  "id": "ui-en-basic",
  "locale": "en",
  "category": "ui",
  "prompt": "How can I renew my Emirates ID?",
  "expected_response": "## Step-by-Step Guide...",
  "expectation": "The chatbot should respond with clear guidance...",
  "negative_expectation": "Must not be off-topic or fabricated...",
  "type": "public_service_query"
}
```

## Test Reports

HTML reports are automatically generated in `test-reports/` with:
- Dashboard statistics (Total, Passed, Failed, Pass Rate)
- Side-by-side comparison with diff highlighting
- Semantic similarity scores
- Filter by status (All/Passed/Failed)

Report path is printed at the end of test execution.

## Development

```bash
# Code quality
make format      # Format code
make lint        # Lint code
make type-check  # Type checking
make check       # Run all checks
```

### Adding Test Cases

1. Add test case to `tests/test_data/data.json`
2. Include: `id`, `category`, `type`, `prompt`, `expected_response`, `expectation`, `negative_expectation`

## Configuration Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SIMAI_ENV` | Environment (dev/stage/prod) | Yes |
| `SIMAI_BASE_URL` | Application base URL | Yes |
| `SIMAI_USER_EMAIL` | Login email | Yes |
| `SIMAI_USER_PASSWORD` | Login password | Yes |
| `SIMAI_SEMANTIC_MODEL` | HuggingFace model | Yes |
| `SIMAI_SEMANTIC_POS_THRESHOLD` | Positive threshold (0.0-1.0) | Yes |
| `SIMAI_SEMANTIC_NEG_THRESHOLD` | Negative threshold (0.0-1.0) | Yes |
| `SIMAI_TIMEOUT_SECONDS` | Request timeout | Yes |

## Notes

- **Semantic Model**: Use multilingual models (e.g., `paraphrase-multilingual-MiniLM-L12-v2`) for Arabic support
- **Thresholds**: Higher `pos_threshold` = stricter matching; Lower `neg_threshold` = stricter negative matching

## Contributing

1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Run `make check` before committing

## License

MIT License
