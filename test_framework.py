from dataclasses import dataclass, field

from llm_client import call_and_log_messages


@dataclass
class TestDefinition:
    query: str
    system: str | None = None  # system prompt passed to the model
    context: list = field(default_factory=list)  # list of {'role': ..., 'content': ...}
    must_have_tokens: list = field(default_factory=list)  # ALL must appear in the response
    could_contain_tokens: list = field(default_factory=list)  # at least ONE must appear
    excluded_tokens: list = field(default_factory=list)
    expected_tone: list = field(default_factory=list)  # e.g. ['friendly', 'concise']


@dataclass
class TestResult:
    response: str
    passed: bool
    must_have_found: list
    must_have_missing: list
    could_contain_found: list
    excluded_tokens_found: list
    tone_passed: bool | None  # None if no expected_tone provided
    tone_response: str | None


def execute_test(test: TestDefinition, model="claude-haiku-4-5") -> TestResult:
    # Build message list: context + query
    messages = list(test.context) + [{"role": "user", "content": test.query}]
    kwargs = {"model": model}
    if test.system is not None:
        kwargs["system"] = test.system
    record = call_and_log_messages(messages, **kwargs)

    if record["status"] != "success":
        raise RuntimeError(f"LLM call failed: {record['error']}")

    response = record["response"]
    response_lower = response.lower()

    # Token checks (case-insensitive)
    must_have_found = [t for t in test.must_have_tokens if t.lower() in response_lower]
    must_have_missing = [t for t in test.must_have_tokens if t.lower() not in response_lower]
    could_contain_found = [t for t in test.could_contain_tokens if t.lower() in response_lower]
    excluded_found = [t for t in test.excluded_tokens if t.lower() in response_lower]

    tokens_pass = (
        not must_have_missing and (not test.could_contain_tokens or len(could_contain_found) > 0) and not excluded_found
    )

    # Tone evaluation
    tone_passed = None
    tone_response = None
    if test.expected_tone:
        tone_descriptor = ", ".join(test.expected_tone)
        tone_prompt = (
            f"Does the following response have a {tone_descriptor} tone? "
            f"Reply with only 'yes' or 'no'.\n\nResponse:\n{response}"
        )
        tone_record = call_and_log_messages([{"role": "user", "content": tone_prompt}], model=model)
        if tone_record["status"] != "success":
            raise RuntimeError(f"Tone evaluation call failed: {tone_record['error']}")
        tone_response = tone_record["response"].strip().lower()
        tone_passed = tone_response.startswith("yes")

    passed = tokens_pass and (tone_passed is not False)

    return TestResult(
        response=response,
        passed=passed,
        must_have_found=must_have_found,
        must_have_missing=must_have_missing,
        could_contain_found=could_contain_found,
        excluded_tokens_found=excluded_found,
        tone_passed=tone_passed,
        tone_response=tone_response,
    )


def validate_results(test: TestDefinition, result: TestResult) -> None:
    """Assert that result meets the expectations in test. Raises AssertionError on failure."""
    if test.must_have_tokens:
        assert not result.must_have_missing, f"Required tokens missing from response: {result.must_have_missing}"

    if test.could_contain_tokens:
        assert result.could_contain_found, (
            f"Expected at least one of {test.could_contain_tokens} in response, but none were found."
        )

    if test.excluded_tokens:
        assert not result.excluded_tokens_found, f"Excluded tokens found in response: {result.excluded_tokens_found}"

    if test.expected_tone:
        assert result.tone_passed, (
            f"Tone check failed. Expected tone: {test.expected_tone}. LLM response: '{result.tone_response}'"
        )
