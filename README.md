# ai-test-framework

A lightweight framework for testing LLM prompts against Claude. Defines structured test cases with token, tone, and injection-resistance checks, and logs every API call for analysis.

## Setup

```sh
git clone <repo>
cd ai-test-framework
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure git hooks:

```sh
git config core.hooksPath .githooks
```

Create a `.env` file with your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Running tests

```sh
source venv/bin/activate
pytest tests/
```

Run a specific test file:

```sh
pytest tests/quiz_tests.py
```

Run with verbose output:

```sh
pytest tests/ -v
```

> **Note:** Tests call the Anthropic API and consume tokens. Each test suite run makes multiple API calls — one for the main response and one for the tone evaluation.

## Project structure

```
llm_client.py         # Anthropic API wrapper with JSONL request logging
test_framework.py     # TestDefinition, execute_test, validate_results
tests/
  quiz_tests.py       # Example test suite for a quiz prompt
logs/                 # Daily JSONL logs of all API calls (gitignored)
scripts/
  run_prompts.py      # Ad-hoc single-prompt runner
  run_messages.py     # Ad-hoc multi-message runner
  analyze_logs.py     # Log analysis: success rate, latency, token usage
```

## Writing tests

Define a `TestDefinition` and pass it to `execute_test` and `validate_results`:

```python
from test_framework import TestDefinition, execute_test, validate_results

test = TestDefinition(
    system="You are a helpful quiz assistant...",  # optional system prompt
    context=[],                                    # optional prior conversation turns
    query="User category: Science",                # the user message under test
    must_have_tokens=["Question 1", "Question 2"], # ALL must appear in response
    could_contain_tokens=["telescope", "physics"], # at least ONE must appear
    excluded_tokens=["Mona Lisa", "van Gogh"],     # NONE may appear in response
    expected_tone=["educational", "clear"],        # tone checked via second LLM call
)
result = execute_test(test)
validate_results(test, result)
```

### Fields

| Field | Description |
|---|---|
| `query` | The user message sent to the model |
| `system` | Optional system prompt passed to `messages.create()` |
| `context` | Optional list of `{"role": ..., "content": ...}` prior turns |
| `must_have_tokens` | All tokens must appear in the response (case-insensitive) |
| `could_contain_tokens` | At least one token must appear; skip check if list is empty |
| `excluded_tokens` | Test fails if any of these appear in the response |
| `expected_tone` | List of tone descriptors evaluated by a second LLM call |

## Logging

Every API call is appended to a daily JSONL file in `logs/`. To summarize:

```sh
python analyze_logs.py
```

Output includes total calls, success rate, error count, average/P95 latency, and total token usage.

## Linting

[ruff](https://docs.astral.sh/ruff/) is configured in `pyproject.toml` (pycodestyle + pyflakes + isort, line length 120). Long lines in `tests/` are exempt since prompt strings can't be wrapped.

```sh
ruff check .
ruff format .
```
