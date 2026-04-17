import base64
import json
import mimetypes
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib import error, request


SUPPORTED_STYLES = [
    "Storyteller",
    "Growth Reflection",
    "Warm Diary",
    "Playful Lifestyle",
]

JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", re.DOTALL)


class ModelProviderError(RuntimeError):
    pass


@dataclass
class ModelConfig:
    provider: str
    api_key: Optional[str]
    base_url: str
    vision_model: str
    text_model: str
    timeout_seconds: int
    use_llm: bool
    fallback_reason: Optional[str] = None


def get_model_config() -> ModelConfig:
    provider = os.getenv("MODEL_PROVIDER", "auto").strip().lower()
    api_key = os.getenv("ARK_API_KEY")
    base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
    shared_model = os.getenv("ARK_MODEL", "").strip()
    vision_model = os.getenv("ARK_VISION_MODEL", "").strip() or shared_model
    text_model = os.getenv("ARK_TEXT_MODEL", "").strip() or shared_model
    timeout_seconds = int(os.getenv("MODEL_TIMEOUT_SECONDS", "90"))

    if provider == "heuristic":
        return ModelConfig(
            provider="heuristic",
            api_key=None,
            base_url=base_url,
            vision_model=vision_model,
            text_model=text_model,
            timeout_seconds=timeout_seconds,
            use_llm=False,
            fallback_reason="MODEL_PROVIDER=heuristic",
        )

    if not api_key:
        return ModelConfig(
            provider="heuristic",
            api_key=None,
            base_url=base_url,
            vision_model=vision_model,
            text_model=text_model,
            timeout_seconds=timeout_seconds,
            use_llm=False,
            fallback_reason="Missing ARK_API_KEY",
        )

    if not vision_model or not text_model:
        return ModelConfig(
            provider="heuristic",
            api_key=None,
            base_url=base_url,
            vision_model=vision_model,
            text_model=text_model,
            timeout_seconds=timeout_seconds,
            use_llm=False,
            fallback_reason="Missing ARK_MODEL or explicit ARK_VISION_MODEL / ARK_TEXT_MODEL",
        )

    return ModelConfig(
        provider="ark-openai-compatible",
        api_key=api_key,
        base_url=base_url,
        vision_model=vision_model,
        text_model=text_model,
        timeout_seconds=timeout_seconds,
        use_llm=True,
    )


def generation_info(config: ModelConfig, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    info = {
        "provider": config.provider,
        "use_llm": config.use_llm,
        "vision_model": config.vision_model if config.use_llm else None,
        "text_model": config.text_model if config.use_llm else None,
        "fallback_reason": config.fallback_reason,
    }
    if overrides:
        info.update(overrides)
    return info


def _data_url_for_file(file_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(file_path.name)
    mime_type = mime_type or "image/jpeg"
    encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _post_chat_completion(config: ModelConfig, model: str, messages: List[Dict[str, Any]], temperature: float) -> str:
    if not config.api_key:
        raise ModelProviderError("Missing API key for model call.")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    req = request.Request(
        f"{config.base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=config.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise ModelProviderError(f"Model request failed with HTTP {exc.code}: {error_body}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ModelProviderError(f"Model request failed: {exc}") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelProviderError(f"Unexpected model response: {body}") from exc

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if "text" in item:
                    parts.append(item["text"])
                elif "content" in item:
                    parts.append(item["content"])
        content = "\n".join(parts)

    if not isinstance(content, str):
        raise ModelProviderError(f"Unsupported content payload: {content}")
    return content.strip()


def _extract_json_payload(raw_text: str) -> Dict[str, Any]:
    match = JSON_BLOCK_PATTERN.search(raw_text)
    candidate = match.group(1) if match else raw_text

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ModelProviderError(f"Model did not return JSON: {raw_text}")

    json_text = candidate[start : end + 1]
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ModelProviderError(f"Model returned invalid JSON: {raw_text}") from exc


def analyze_image_with_llm(
    config: ModelConfig,
    *,
    file_path: Path,
    title: str,
    context: str,
    language: str,
    role_label: str,
) -> Dict[str, Any]:
    output_language = "Chinese" if language == "zh" else "English"
    prompt = f"""
You are helping a social storytelling product understand one photo from a user's photo set.

User title: {title}
User context: {context or "No additional context."}
Role of this image inside the set: {role_label}
Output language: {output_language}

Return strict JSON only:
{{
  "analysis_text": "1-2 natural sentences for internal use. No mention of pixels, brightness numbers, file names, timestamps, or generic wording like 'this frame'.",
  "mood_tag": "uplifting|reflective|steady",
  "subject_hint": "short phrase capturing the most relevant visible subject"
}}

Rules:
- Focus on what is visually plausible and socially meaningful.
- If context mentions a brand or event, use it only when the image plausibly supports it.
- Keep the wording concise and human.
""".strip()

    messages = [
        {"role": "system", "content": "You are a precise multimodal analyst. Return JSON only."},
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": _data_url_for_file(file_path)}},
                {"type": "text", "text": prompt},
            ],
        },
    ]
    raw_text = _post_chat_completion(config, config.vision_model, messages, temperature=0.2)
    parsed = _extract_json_payload(raw_text)

    return {
        "analysis_text": str(parsed.get("analysis_text", "")).strip(),
        "mood_tag": str(parsed.get("mood_tag", "steady")).strip() or "steady",
        "subject_hint": str(parsed.get("subject_hint", "")).strip(),
    }


def generate_story_with_llm(
    config: ModelConfig,
    *,
    language: str,
    title: str,
    context: str,
    profile: Dict[str, Any],
    retrieved_memories: Sequence[Dict[str, Any]],
    asset_briefs: Sequence[Dict[str, Any]],
    fallback_story: Dict[str, Any],
) -> Dict[str, Any]:
    output_language = "Chinese" if language == "zh" else "English"
    memory_summary = [
        {
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "emotion": item.get("emotion", ""),
            "growth_signal": item.get("growth_signal", ""),
        }
        for item in retrieved_memories[:3]
    ]
    asset_summary = [
        {
            "file_name": item.get("file_name", ""),
            "analysis_text": item.get("analysis_text", ""),
            "mood_tag": item.get("mood_tag", ""),
            "subject_hint": item.get("metadata", {}).get("subject_hint", ""),
            "role": item.get("metadata", {}).get("role", ""),
        }
        for item in asset_briefs
    ]

    prompt = f"""
You are the writing brain of a social storytelling agent. You turn a photo collection into publishable social posts.

Output language: {output_language}
Collection title: {title}
User context: {context or "No additional context."}
Preferred styles ranking: {profile.get("top_styles", [])}
Preference summary: {profile.get("summary", "")}
Preference tags: {profile.get("top_tags", [])}
Voice notes: {profile.get("voice_notes", [])}
Retrieved memories: {json.dumps(memory_summary, ensure_ascii=False)}
Image analysis briefs: {json.dumps(asset_summary, ensure_ascii=False)}
Fallback story draft: {json.dumps(fallback_story, ensure_ascii=False)}

Return strict JSON only with this shape:
{{
  "story_summary": "2-4 natural sentences summarizing the collection",
  "narrative_arc": "1 concise sentence",
  "emotional_tone": "short human-readable phrase in the output language",
  "growth_signal": "short human-readable phrase in the output language",
  "themes": ["theme1", "theme2", "theme3"],
  "posts": [
    {{"style_name": "Storyteller", "hook": "...", "content": "..."}},
    {{"style_name": "Growth Reflection", "hook": "...", "content": "..."}},
    {{"style_name": "Warm Diary", "hook": "...", "content": "..."}},
    {{"style_name": "Playful Lifestyle", "hook": "...", "content": "..."}}
  ]
}}

Rules:
- Keep style_name exactly as listed above.
- The posts must read like real publishable copy, not analysis notes.
- Do not mention file names, timestamps, brightness values, or phrases like "this frame".
- Use the retrieved memories subtly, only when they truly help continuity.
- If the user's language is Chinese, write fully natural Chinese.
- Keep hashtags in the same language as the post and no more than 4.
""".strip()

    messages = [
        {"role": "system", "content": "You are a high-quality social copywriter. Return JSON only."},
        {"role": "user", "content": prompt},
    ]
    raw_text = _post_chat_completion(config, config.text_model, messages, temperature=0.7)
    parsed = _extract_json_payload(raw_text)

    posts = parsed.get("posts")
    if not isinstance(posts, list):
        raise ModelProviderError(f"Model response did not include posts: {raw_text}")

    normalized_posts = []
    by_style = {str(item.get("style_name", "")).strip(): item for item in posts if isinstance(item, dict)}
    for style_name in SUPPORTED_STYLES:
        item = by_style.get(style_name)
        if not item:
            raise ModelProviderError(f"Model response missed style '{style_name}': {raw_text}")
        normalized_posts.append(
            {
                "style_name": style_name,
                "hook": str(item.get("hook", "")).strip(),
                "content": str(item.get("content", "")).strip(),
            }
        )

    themes = parsed.get("themes", [])
    if not isinstance(themes, list):
        themes = []

    return {
        "story_summary": str(parsed.get("story_summary", "")).strip() or fallback_story["story_summary"],
        "narrative_arc": str(parsed.get("narrative_arc", "")).strip() or fallback_story["narrative_arc"],
        "emotional_tone": str(parsed.get("emotional_tone", "")).strip() or fallback_story["emotional_tone"],
        "growth_signal": str(parsed.get("growth_signal", "")).strip() or fallback_story["growth_signal"],
        "themes": [str(item).strip() for item in themes if str(item).strip()][:5] or fallback_story["themes"],
        "posts": normalized_posts,
    }
