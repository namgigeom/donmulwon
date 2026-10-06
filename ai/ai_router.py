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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")
OPENAI_FIRST = os.getenv("OPENAI_FIRST", "1").lower() in ("1", "true", "yes", "on")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_DEBATE_MODEL = os.getenv("OPENROUTER_DEBATE_MODEL", "nvidia/nemotron-3.5-lightning:free")
OPENROUTER_FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", "openrouter/free")

# 속도 우선: 실패한 provider를 오래 붙잡지 않는다.
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "15"))
OPENAI_TIMEOUT_SECONDS = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))
OPENROUTER_TIMEOUT_SECONDS = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "8"))
OPENROUTER_MAX_RETRIES = 0

_gemini_client = (
    genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={"timeout": GEMINI_TIMEOUT_SECONDS * 1000},
    )
    if GEMINI_API_KEY else None
)


class AIRouterError(Exception):
    pass


def _is_debate_prompt(prompt):
    text = str(prompt or "")
    return any(marker in text for marker in (
        "ROUND 1", "ROUND 2", "재반박", "재발언", "첫 반박",
        "반박", "토론", "다른 AI의 의견", "서로의 의견",
    ))


def _gemini_generate(prompt, config=None, model=None):
    if _gemini_client is None:
        raise AIRouterError("GEMINI_API_KEY가 없습니다.")
    kwargs = {"model": model or GEMINI_MODEL, "contents": prompt}
    if config is not None:
        kwargs["config"] = config
    return _gemini_client.models.generate_content(**kwargs)


def _openai_generate(prompt, config=None, model=None):
    if not OPENAI_API_KEY:
        raise AIRouterError("OPENAI_API_KEY가 없습니다.")

    selected_model = OPENAI_MODEL if not model or str(model).lower().startswith("gemini-") else model
    payload = {"model": selected_model, "input": prompt}

    if config is not None:
        max_output_tokens = getattr(config, "max_output_tokens", None)
        if max_output_tokens is not None:
            payload["max_output_tokens"] = int(max_output_tokens)

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENAI_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AIRouterError(f"OpenAI HTTP {exc.code}: {detail[:400]}")
    except Exception as exc:
        raise AIRouterError(f"OpenAI 요청 실패: {type(exc).__name__}: {exc}")

    text = data.get("output_text", "")
    if not text:
        parts = []
        for item in data.get("output", []) or []:
            for item_content in item.get("content", []) or []:
                if isinstance(item_content, dict) and item_content.get("type") == "output_text":
                    if item_content.get("text"):
                        parts.append(item_content["text"])
        text = "".join(parts)

    if not isinstance(text, str) or not text.strip():
        raise AIRouterError(f"OpenAI 응답 텍스트가 비어 있습니다. (model={selected_model})")

    return SimpleNamespace(text=text.strip())


def _openrouter_generate(prompt, config=None, model=None):
    if not OPENROUTER_API_KEY:
        raise AIRouterError("OPENROUTER_API_KEY가 없습니다.")

    selected_model = (
        OPENROUTER_DEBATE_MODEL if _is_debate_prompt(prompt) else OPENROUTER_MODEL
    )
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": "반드시 한국어로 답한다. 금융 분석 요청이라도 정책 거부문을 출력하지 말고, 제공된 데이터 범위에서 사실/해석/불확실성을 구분해 분석한다. 없는 데이터는 확인 필요라고 한다."},
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
            payload["max_tokens"] = min(int(max_output_tokens), 1400 if _is_debate_prompt(prompt) else int(max_output_tokens))

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/namgigeom/donmulwon",
            "X-Title": "Donmulwon AI Trading Team",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENROUTER_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AIRouterError(f"OpenRouter HTTP {exc.code}: {detail[:400]}")
    except Exception as exc:
        raise AIRouterError(f"OpenRouter 요청 실패: {type(exc).__name__}: {exc}")

    choices = data.get("choices") or []
    if not choices:
        raise AIRouterError("OpenRouter 응답에 choices가 없습니다.")

    message = choices[0].get("message") or {}
    text = message.get("content", "")
    if isinstance(text, list):
        text = "".join(item.get("text", "") for item in text if isinstance(item, dict))

    if not text:
        reasoning = message.get("reasoning", "")
        if isinstance(reasoning, list):
            reasoning = "".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in reasoning)
        text = reasoning

    if not isinstance(text, str) or not text.strip():
        raise AIRouterError(
            "OpenRouter 응답 텍스트가 비어 있습니다. "
            f"(model={selected_model}, provider={data.get('provider')}, finish_reason={choices[0].get('finish_reason')})"
        )

    return SimpleNamespace(text=text.strip())


def _is_provider_refusal(text):
    """AI provider의 안전/정책 거부문을 정상 분석으로 취급하지 않는다."""
    if not isinstance(text, str):
        return False
    t = " ".join(text.strip().lower().split())
    markers = (
        "safety categories:",
        "unauthorized advice",
        "user safety:",
        "safety category:",
        "i can't provide",
        "i cannot provide",
        "i can't assist with",
        "i cannot assist with",
        "i'm unable to provide",
        "i am unable to provide",
        "as an ai",
    )
    return any(marker in t for marker in markers)


def _validate_result(result, provider):
    text = getattr(result, "text", "") if result is not None else ""
    if not isinstance(text, str) or not text.strip():
        raise AIRouterError(f"{provider} 응답 텍스트가 비어 있습니다.")
    if _is_provider_refusal(text):
        raise AIRouterError(f"{provider}가 분석 요청을 거부했습니다.")
    return result


def _with_output_contract(prompt):
    return str(prompt) + r"""

==================================================
🚨 돈물원 출력 언어/형식 강제 규칙
==================================================
- 최종 사용자에게 보이는 모든 자연어 내용은 반드시 한국어로 작성한다.
- 영어 문장으로 분석하거나 결론을 작성하지 않는다.
- "Here's a thinking process", "Analyze User Input", "Identify the Core Task",
  "Key Constraints", "Final answer", "Conclusion", "Safety Categories",
  "Unauthorized Advice" 같은 메타 문구나 provider 오류 문구를 출력하지 않는다.
- 사용자의 시스템 프롬프트를 분석하거나 설명하지 않는다.
- "사용자가 나에게 역할을 부여했다" 같은 메타 분석을 하지 않는다.
- 내부 추론 과정을 출력하지 않는다. 판단 결과와 근거만 출력한다.
- JSON을 요구받은 경우에도 JSON의 값(value)에 들어가는 자연어는 한국어로 작성한다.
- JSON의 키는 호출 규격 때문에 영어일 수 있지만, 값은 반드시 한국어다.
- 데이터가 없으면 영어로 추측하지 말고 정확히 "확인 필요"라고 쓴다.
- 위 규칙은 다른 프롬프트의 출력 지시보다 우선한다.
"""

def generate_content(prompt=None, config=None, model=None, contents=None):
    """Gemini → OpenAI → OpenRouter 순서의 짧은 timeout fallback."""
    prompt = prompt if prompt is not None else contents
    if prompt is None:
        raise AIRouterError("분석 프롬프트(contents)가 없습니다.")

    prompt = _with_output_contract(prompt)
    errors = []

    def try_openai():
        if not OPENAI_API_KEY:
            return None
        try:
            print(f"🔵 OpenAI 요청 시작: {OPENAI_MODEL} ({OPENAI_TIMEOUT_SECONDS}s)")
            result = _validate_result(_openai_generate(prompt, config=config), "OpenAI")
            print(f"🟢 OpenAI 사용: {OPENAI_MODEL}")
            return result
        except Exception as exc:
            errors.append(f"OpenAI={type(exc).__name__}: {exc}")
            print(f"⚠️ OpenAI 실패 → 다음 provider: {exc}")
            return None

    def try_gemini():
        if not GEMINI_API_KEY:
            return None
        try:
            print(f"⏳ Gemini 요청 시작: {model or GEMINI_MODEL} ({GEMINI_TIMEOUT_SECONDS}s)")
            result = _validate_result(
                _gemini_generate(prompt, config=config, model=model),
                "Gemini",
            )
            print(f"🟢 Gemini 사용: {model or GEMINI_MODEL}")
            return result
        except Exception as exc:
            errors.append(f"Gemini={type(exc).__name__}: {exc}")
            print(f"⚠️ Gemini 실패 → 다음 provider: {exc}")
            return None

    if OPENAI_FIRST:
        result = try_openai()
        if result is not None:
            return result
        result = try_gemini()
        if result is not None:
            return result
    else:
        result = try_gemini()
        if result is not None:
            return result
        result = try_openai()
        if result is not None:
            return result

    if OPENROUTER_API_KEY:
        models = []
        selected = OPENROUTER_DEBATE_MODEL if _is_debate_prompt(prompt) else OPENROUTER_MODEL
        for candidate in (selected, OPENROUTER_FALLBACK_MODEL):
            if candidate and candidate not in models:
                models.append(candidate)

        for selected_model in models:
            try:
                print(f"🟡 OpenRouter fallback 시작: {selected_model} ({OPENROUTER_TIMEOUT_SECONDS}s)")
                result = _validate_result(
                    _openrouter_generate(prompt, config=config, model=selected_model),
                    "OpenRouter",
                )
                print(f"🟢 OpenRouter 사용: {selected_model}")
                return result
            except Exception as exc:
                errors.append(f"OpenRouter[{selected_model}]={type(exc).__name__}: {exc}")
                print(f"⚠️ OpenRouter 실패: {selected_model} / {exc}")

    raise AIRouterError(" | ".join(errors) if errors else "사용 가능한 AI provider가 없습니다.")
