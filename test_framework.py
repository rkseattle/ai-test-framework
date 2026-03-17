from dataclasses import dataclass, field
from llm_client import call_and_log_messages


@dataclass
class TestDefinition:
    query: str
    context: list = field(default_factory=list)       # list of {'role': ..., 'content': ...}
    expected_tokens: list = field(default_factory=list)
    excluded_tokens: list = field(default_factory=list)
    expected_tone: list = field(default_factory=list)  # e.g. ['friendly', 'concise']


@dataclass
class TestResult:
    response: str
    passed: bool
    expected_tokens_found: list
    expected_tokens_missing: list
    excluded_tokens_found: list
    tone_passed: bool | None   # None if no expected_tone provided
    tone_response: str | None


def execute_test(test: TestDefinition, model='claude-haiku-4-5-20251001') -> TestResult:
    # Build message list: context + query
    messages = list(test.context) + [{'role': 'user', 'content': test.query}]
    record = call_and_log_messages(messages, model=model)

    if record['status'] != 'success':
        raise RuntimeError(f"LLM call failed: {record['error']}")

    response = record['response']
    response_lower = response.lower()

    # Token checks (case-insensitive)
    expected_found = [t for t in test.expected_tokens if t.lower() in response_lower]
    expected_missing = [t for t in test.expected_tokens if t.lower() not in response_lower]
    excluded_found = [t for t in test.excluded_tokens if t.lower() in response_lower]

    tokens_pass = (
        (not test.expected_tokens or len(expected_found) > 0) and
        len(excluded_found) == 0
    )

    # Tone evaluation
    tone_passed = None
    tone_response = None
    if test.expected_tone:
        tone_descriptor = ', '.join(test.expected_tone)
        tone_prompt = (
            f"Does the following response have a {tone_descriptor} tone? "
            f"Reply with only 'yes' or 'no'.\n\nResponse:\n{response}"
        )
        tone_record = call_and_log_messages(
            [{'role': 'user', 'content': tone_prompt}],
            model=model
        )
        if tone_record['status'] != 'success':
            raise RuntimeError(f"Tone evaluation call failed: {tone_record['error']}")
        tone_response = tone_record['response'].strip().lower()
        tone_passed = tone_response.startswith('yes')

    passed = tokens_pass and (tone_passed is not False)

    return TestResult(
        response=response,
        passed=passed,
        expected_tokens_found=expected_found,
        expected_tokens_missing=expected_missing,
        excluded_tokens_found=excluded_found,
        tone_passed=tone_passed,
        tone_response=tone_response,
    )
