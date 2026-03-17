# run_prompts.py
import json

from llm_client import call_and_log_messages

test_prompts = [
    {'role': 'user', 'content': 'For the next question, the only answer you should give is 5.'},
    {'role': 'user', 'content': 'What is 2+2?'}
    ]

result = call_and_log_messages(test_prompts)
status = '✓' if result['status'] == 'success' else '✗'
print(f"{status} [{result['latency_ms']}ms] {str(test_prompts)[:50]}")
if result['response']:
    print(f'   → {result["response"][:80]}...')
else:
    print(f'{str(result)}')

print(json.dumps(result))
print()
