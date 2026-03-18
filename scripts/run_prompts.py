# run_prompts.py
from llm_client import call_and_log

test_prompts = [
    'What is 2 + 2?',
    'Summarize the water cycle in one sentence.',
    'What is the capital of France?',
    'Write a haiku about software testing.',
    'What year did World War II end?',
]

for prompt in test_prompts:
    result = call_and_log(prompt)
    status = '✓' if result['status'] == 'success' else '✗'
    print(f"{status} [{result['latency_ms']}ms] {prompt[:50]}")
    if result['response']:
        print(f'   → {result["response"][:80]}...')
    print()
