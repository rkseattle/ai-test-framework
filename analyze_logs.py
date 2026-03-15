import json, glob
from pathlib import Path

records = []
for file in glob.glob('logs/*.jsonl'):
    with open(file) as f:
        for line in f:
            records.append(json.loads(line))

successes = [r for r in records if r['status'] == 'success']
errors    = [r for r in records if r['status'] == 'error']
latencies = [r['latency_ms'] for r in successes]

print(f'Total calls:    {len(records)}')
print(f'Success rate:   {len(successes)/len(records)*100:.1f}%')
print(f'Error count:    {len(errors)}')
print(f'Avg latency:    {sum(latencies)/len(latencies):.0f}ms')
print(f'P95 latency:    {sorted(latencies)[int(len(latencies)*0.95)]:.0f}ms')
total_in  = sum(r['input_tokens']  or 0 for r in successes)
total_out = sum(r['output_tokens'] or 0 for r in successes)
print(f'Total tokens:   {total_in + total_out:,} (in: {total_in:,} out: {total_out:,})')