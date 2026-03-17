# llm_client.py
import anthropic, json, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic()

def call_and_log(prompt: str, model='claude-haiku-4-5-20251001',
                 system='You are a helpful assistant.',
                 max_tokens=1024) -> dict:
    call_id = str(uuid.uuid4())[:8]
    start   = time.time()

    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{'role': 'user', 'content': prompt}]
        )
        latency_ms = round((time.time() - start) * 1000)
        response_text = message.content[0].text
        status = 'success'
        error = None
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000)
        response_text = None
        status = 'error'
        error = str(e)
        message = None

    record = {
        'call_id':       call_id,
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'model':         model,
        'system':        system,
        'prompt':        prompt,
        'response':      response_text,
        'status':        status,
        'error':         error,
        'latency_ms':    latency_ms,
        'input_tokens':  message.usage.input_tokens  if message else None,
        'output_tokens': message.usage.output_tokens if message else None,
    }

    # Append to daily log file
    log_file = LOG_DIR / f'{datetime.now().strftime("%Y-%m-%d")}.jsonl'
    with open(log_file, 'a') as f:
        f.write(json.dumps(record) + '\n')

    return record

def call_and_log_messages(messages: list, model='claude-haiku-4-5-20251001',
                 system='You are a helpful assistant.',
                 max_tokens=1024) -> dict:
    call_id = str(uuid.uuid4())[:8]
    start   = time.time()

    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        latency_ms = round((time.time() - start) * 1000)
        response_text = message.content[0].text
        status = 'success'
        error = None
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000)
        response_text = None
        status = 'error'
        error = str(e)
        message = None

    record = {
        'call_id':       call_id,
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'model':         model,
        'system':        system,
        'messages':      messages,
        'response':      response_text,
        'status':        status,
        'error':         error,
        'latency_ms':    latency_ms,
        'input_tokens':  message.usage.input_tokens  if message else None,
        'output_tokens': message.usage.output_tokens if message else None,
    }

    # Append to daily log file
    log_file = LOG_DIR / f'{datetime.now().strftime("%Y-%m-%d")}.jsonl'
    with open(log_file, 'a') as f:
        f.write(json.dumps(record) + '\n')

    return record