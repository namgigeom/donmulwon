import os
import time
import json
import urllib.request
import urllib.error
from types import SimpleNamespace

from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

GEMINI_MAX_RETRIES = 1
OPENROUTER_MAX_RETRIES = 2

_gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


class AIRouterError(Exception):
    pass


def _is_fallback_error(exc):
    text = str(exc).lower()
    return any(token in text for token in [
        "429", "resource_exhausted", "quota", "503", "502", "504",
        "unavailable", "high demand", "rate limit"
    ])


def _gemini_generate(prompt, config=None):
    if _gemini_client is None:
        raise AIRouterError("GEMINI_API_KEY가 없습니다.")

    kwargs = {"model": GEMINI_MODEL, "contents": prompt}
    if config is not None:
        kwargs["config"] = config

    return _gemini_client.models.generate_content(**kwargs)


def _openrouter_generate(prompt, config=None):
    if not OPENROUTER_API_KEY:
        raise AIRouterError("OPENROUTER_API_KEY가 없습니다.")

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI investment analysis assistant. Answer in Korean unless explicitly requested otherwise."
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    if config is not None:
        temperature = getattr(config, "temperature", None)
        max_output_tokens = getattr(config, "max_output_tokens", None)
        if temperature is not None:
            payload["temperature"] = temperature
        if max_output_tokens is not None:
            payload["max_tokens"] = max_output_tokens

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/namgigeom/donmulwon",
            "X-Title": "Donmulwon AI Trading Team",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AIRouterError(f"OpenRouter HTTP {exc.code}: {detail[:500]}")
    except Exception as exc:
        raise AIRouterError(f"OpenRouter 요청 실패: {exc}")

    choices = data.get("choices", [])
    if not choices:
        raise AIRouterError("OpenRouter 응답에 choices가 없습니다.")

    text = choices[0].get("message", {}).get("content", "")
    if not text:
        raise AIRouterError("OpenRouter 응답 텍스트가 비어 있습니다.")

    return SimpleNamespace(text=text)


def generate_content(prompt, config=None):
    """Gemini 우선 → quota/429/503 등 발생 시 OpenRouter 자동 fallback."""
    gemini_error = None

    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            result = _gemini_generate(prompt, config)
            print("🟢 Gemini 사용")
            return result
        except Exception as exc:
            gemini_error = exc
            if attempt < GEMINI_MAX_RETRIES and not _is_fallback_error(exc):
                time.sleep(1)
                continue
            break

    print("🟡 Gemini 한도/장애 감지 → OpenRouter 자동 전환")

    openrouter_error = None
    for attempt in range(OPENROUTER_MAX_RETRIES + 1):
        try:
            result = _openrouter_generate(prompt, config)
            print(f"🟢 OpenRouter 사용: {OPENROUTER_MODEL}")
            return result
        except Exception as exc:
            openrouter_error = exc
            if attempt < OPENROUTER_MAX_RETRIES:
                time.sleep(min(2 ** attempt, 4))

    raise AIRouterError(
        f"Gemini 실패: {gemini_error}\nOpenRouter 실패: {openrouter_error}"
    )
