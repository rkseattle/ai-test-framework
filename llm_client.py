# llm_client.py
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import openai
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_anthropic_client = None
_openai_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI()
    return _openai_client


def _is_openai_model(model: str) -> bool:
    return model.startswith(("gpt-", "o1", "o3", "o4", "text-"))


def _call_anthropic(messages: list, model: str, system: str, max_tokens: int):
    message = _get_anthropic_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    text_blocks = [b.text for b in message.content if hasattr(b, "text")]
    response_text = text_blocks[-1] if text_blocks else None
    return response_text, message.usage.input_tokens, message.usage.output_tokens


def _call_openai(messages: list, model: str, system: str, max_tokens: int):
    full_messages = [{"role": "system", "content": system}] + messages
    response = _get_openai_client().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=full_messages,
    )
    response_text = response.choices[0].message.content if response.choices else None
    return response_text, response.usage.prompt_tokens, response.usage.completion_tokens


def _log_record(record: dict):
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")


def call_and_log(
    prompt: str, model="claude-haiku-4-5-20251001", system="You are a helpful assistant.", max_tokens=1024
) -> dict:
    return call_and_log_messages(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        system=system,
        max_tokens=max_tokens,
        prompt=prompt,
    )


def call_and_log_messages(
    messages: list,
    model="claude-haiku-4-5-20251001",
    system="You are a helpful assistant.",
    max_tokens=1024,
    prompt=None,
) -> dict:
    call_id = str(uuid.uuid4())[:8]
    start = time.time()

    try:
        if _is_openai_model(model):
            response_text, input_tokens, output_tokens = _call_openai(messages, model, system, max_tokens)
        else:
            response_text, input_tokens, output_tokens = _call_anthropic(messages, model, system, max_tokens)
        latency_ms = round((time.time() - start) * 1000)
        status = "success"
        error = None
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000)
        response_text = None
        input_tokens = None
        output_tokens = None
        status = "error"
        error = str(e)

    record = {
        "call_id": call_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "system": system,
        "prompt": prompt,
        "messages": messages,
        "response": response_text,
        "status": status,
        "error": error,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    _log_record(record)
    return record
