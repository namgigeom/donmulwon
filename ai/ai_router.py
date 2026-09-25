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

# 토론은 호출 횟수가 많기 때문에 느린 무료 모델을 무작위로 고르지 않는다.
# 독립 분석은 기존 openrouter/free를 유지하고, 재반박/토론은 빠른 무료 모델을 사용한다.
OPENROUTER_DEBATE_MODEL = os.getenv(
    "OPENROUTER_DEBATE_MODEL",
    "nvidia/nemotron-3.5-lightning:free"
)

GEMINI_MAX_RETRIES = 0
OPENROUTER_MAX_RETRIES = 0
OPENROUTER_TIMEOUT_SECONDS = 20

_gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


class AIRouterError(Exception):
    pass


def _gemini_generate(prompt, config=None, model=None):
    if _gemini_client is None:
        raise AIRouterError("GEMINI_API_KEY가 없습니다.")

    kwargs = {
        "model": model or GEMINI_MODEL,
        "contents": prompt,
    }

    if config is not None:
        kwargs["config"] = config

    return _gemini_client.models.generate_content(**kwargs)


def _is_debate_prompt(prompt):
    text = str(prompt or "")
    markers = [
        "ROUND 1",
        "ROUND 2",
        "재반박",
        "재발언",
        "첫 반박",
        "반박",
        "토론",
        "다른 AI의 의견",
        "서로의 의견",
    ]
    return any(marker in text for marker in markers)


def _openrouter_generate(prompt, config=None, model=None):
    if not OPENROUTER_API_KEY:
        raise AIRouterError("OPENROUTER_API_KEY가 없습니다.")

    selected_model = model or (
        OPENROUTER_DEBATE_MODEL
        if _is_debate_prompt(prompt)
        else OPENROUTER_MODEL
    )

    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI investment analysis assistant. "
                    "Answer in Korean unless explicitly requested otherwise."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    if config is not None:
        temperature = getattr(config, "temperature", None)
        max_output_tokens = getattr(config, "max_output_tokens", None)

        if temperature is not None:
            payload["temperature"] = temperature

        if max_output_tokens is not None:
            # 토론 발언은 장문이 필요 없으므로 무료 모델에서 과도한 생성 방지.
            if _is_debate_prompt(prompt):
                payload["max_tokens"] = min(int(max_output_tokens), 1200)
            else:
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
        with urllib.request.urlopen(
            request,
            timeout=OPENROUTER_TIMEOUT_SECONDS
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AIRouterError(
            f"OpenRouter HTTP {exc.code}: {detail[:500]}"
        )

    except Exception as exc:
        raise AIRouterError(
            f"OpenRouter 요청 실패: {exc}"
        )

    choices = data.get("choices", [])

    if not choices:
        raise AIRouterError(
            "OpenRouter 응답에 choices가 없습니다."
        )

    message = choices[0].get("message", {})
    text = message.get("content", "")

    if isinstance(text, list):
        text = "".join(
            item.get("text", "")
            for item in text
            if isinstance(item, dict)
        )

    if not text:
        raise AIRouterError(
            "OpenRouter 응답 텍스트가 비어 있습니다."
        )

    return SimpleNamespace(text=text)


def generate_content(
    prompt=None,
    config=None,
    model=None,
    contents=None,
):
    """
    Gemini 우선 → Gemini 실패 시 즉시 OpenRouter fallback.

    독립 분석:
        OPENROUTER_MODEL

    토론/재반박:
        OPENROUTER_DEBATE_MODEL

    기존 Google SDK 스타일의 다음 호출 형식을 모두 지원한다.
        generate_content(model="gemini-3.6-flash", contents=prompt)
        generate_content(prompt, config=config)
    """

    if prompt is None:
        prompt = contents

    if prompt is None:
        raise AIRouterError(
            "분석 프롬프트(contents)가 없습니다."
        )

    # --------------------------------------------------------
    # 1. Gemini (키가 있을 때만 시도)
    # --------------------------------------------------------
    gemini_error = None

    if GEMINI_API_KEY:
        gemini_attempts = range(GEMINI_MAX_RETRIES + 1)
    else:
        gemini_attempts = []

    for attempt in gemini_attempts:
        try:
            result = _gemini_generate(
                prompt=prompt,
                config=config,
                model=model,
            )
            print(
                f"🟢 Gemini 사용: {model or GEMINI_MODEL}"
            )
            return result

        except Exception as exc:
            gemini_error = exc

            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(1)

    # --------------------------------------------------------
    # 2. Gemini 실패 → 즉시 OpenRouter
    # --------------------------------------------------------
    selected_model = (
        OPENROUTER_DEBATE_MODEL
        if _is_debate_prompt(prompt)
        else OPENROUTER_MODEL
    )

    if GEMINI_API_KEY:
        print("🟡 Gemini 실패/한도 감지 → OpenRouter 자동 전환")
    else:
        print("🟡 GEMINI_API_KEY 없음 → OpenRouter 사용")

    openrouter_error = None

    for attempt in range(OPENROUTER_MAX_RETRIES + 1):
        try:
            result = _openrouter_generate(
                prompt=prompt,
                config=config,
                model=None,
            )
            print(
                f"🟢 OpenRouter 사용: {selected_model}"
            )
            return result

        except Exception as exc:
            openrouter_error = exc

            if attempt < OPENROUTER_MAX_RETRIES:
                time.sleep(2)

    raise AIRouterError(
        "Gemini 실패: "
        f"{gemini_error}\n"
        "OpenRouter 실패: "
        f"{openrouter_error}"
    )
