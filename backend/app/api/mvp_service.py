import json
import re
import shutil
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from fastapi import UploadFile
from PIL import Image, ImageStat
from sqlmodel import Session

from database import (
    CollectionAsset,
    FeedbackEvent,
    GeneratedPost,
    MemoryItem,
    PhotoCollection,
    User,
    UserPreference,
)
from .model_provider import (
    ModelProviderError,
    analyze_image_with_llm,
    generate_story_with_llm,
    generation_info,
    get_model_config,
)

BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_ROOT = BASE_DIR / "storage" / "media"
UPLOAD_ROOT = MEDIA_ROOT / "uploads"

DEFAULT_STYLE_WEIGHTS = {
    "Storyteller": 1.0,
    "Warm Diary": 0.95,
    "Playful Lifestyle": 0.9,
    "Growth Reflection": 1.0,
}

STYLE_LIBRARY = {
    "Storyteller": {
        "angle": "turn the photo set into a compact narrative with a clear arc",
        "cta": "Which moment in the sequence would you keep the longest?",
    },
    "Warm Diary": {
        "angle": "sound intimate, grounded, and emotionally honest",
        "cta": "Saving this feeling for later.",
    },
    "Playful Lifestyle": {
        "angle": "sound lively, polished, and creator-friendly",
        "cta": "Tiny scenes, big serotonin.",
    },
    "Growth Reflection": {
        "angle": "highlight progress, self-awareness, and continuity across time",
        "cta": "Proof that small chapters still move the story forward.",
    },
}

STYLE_LABEL_ZH = {
    "Storyteller": "叙事感",
    "Warm Diary": "日记感",
    "Playful Lifestyle": "轻分享",
    "Growth Reflection": "成长感",
}

POSITIVE_HINTS = {
    "happy",
    "joy",
    "excited",
    "celebrate",
    "cozy",
    "grateful",
    "family",
    "friend",
    "win",
    "progress",
    "开心",
    "惊喜",
    "礼物",
    "礼品",
    "收到",
    "满足",
    "喜欢",
    "联名",
}
REFLECTIVE_HINTS = {
    "quiet",
    "alone",
    "reset",
    "reflect",
    "night",
    "healing",
    "learn",
    "growth",
    "change",
    "安静",
    "独处",
    "慢慢",
    "沉淀",
    "治愈",
}

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
GENERIC_ENGLISH_TOKENS = {
    "this",
    "that",
    "frame",
    "feels",
    "around",
    "level",
    "brightness",
    "centered",
    "moment",
    "image",
    "photo",
    "story",
    "caption",
    "landscape",
    "portrait",
    "balanced",
    "neutral",
    "steady",
    "use",
    "bigger",
    "rather",
    "final",
    "opening",
    "closing",
    "detail",
    "shot",
    "scene",
    "jpg",
    "jpeg",
    "png",
    "img",
    "dsc",
}
GENERIC_CHINESE_TOKENS = {
    "照片",
    "画面",
    "内容",
    "故事",
    "一下",
    "一个",
    "一些",
    "这次",
    "联名",
    "周边",
}
DEFAULT_TITLE_BY_LANGUAGE = {
    "zh": "这组日常片段",
    "en": "Untitled Moment",
}
EMOTION_DISPLAY = {
    "uplifting": {"zh": "轻松满足", "en": "uplifting"},
    "reflective": {"zh": "安静克制", "en": "reflective"},
    "steady": {"zh": "平稳自然", "en": "steady"},
}
GROWTH_SIGNAL_DISPLAY = {
    "skill-building": {"zh": "技能积累", "en": "skill-building"},
    "connection": {"zh": "关系连接", "en": "connection"},
    "exploration": {"zh": "新鲜体验", "en": "exploration"},
    "self-regulation": {"zh": "自我调节", "en": "self-regulation"},
    "small-joy": {"zh": "日常小确幸", "en": "small joys"},
    "consistency": {"zh": "稳定记录", "en": "consistency"},
}
VALID_MOOD_TAGS = {"uplifting", "reflective", "steady"}


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _load_json(value: str, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _tokenize(text: str) -> List[str]:
    latin_tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    cjk_chunks = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    cjk_tokens: List[str] = []
    for chunk in cjk_chunks:
        cjk_tokens.append(chunk)
        if 2 <= len(chunk) <= 12:
            cjk_tokens.extend(chunk[index : index + 2] for index in range(len(chunk) - 1))
    return latin_tokens + cjk_tokens


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug or "moment"


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _detect_language(*values: str) -> str:
    combined = " ".join(value for value in values if value)
    if CJK_PATTERN.search(combined):
        return "zh"
    return "en"


def _clean_token(token: str) -> Optional[str]:
    cleaned = token.strip().lower()
    if not cleaned:
        return None
    if cleaned.isdigit() or re.fullmatch(r"\d{6,}", cleaned):
        return None
    if cleaned in GENERIC_ENGLISH_TOKENS:
        return None
    return cleaned


def _meaningful_filename_tokens(name: str) -> List[str]:
    tokens = []
    for token in _tokenize(Path(name).stem):
        cleaned = _clean_token(token)
        if cleaned:
            tokens.append(cleaned)
    return tokens[:3]


def _extract_chinese_phrases(text: str) -> List[str]:
    parts = [part.strip() for part in re.split(r"[，。！？；、\n]", text) if part.strip()]
    return [part for part in parts if len(part) >= 2]


def _extract_context_clauses(context: str, language: str) -> List[str]:
    if not context.strip():
        return []
    if language == "zh":
        return _extract_chinese_phrases(context)[:3]

    parts = [part.strip() for part in re.split(r"[.!?;\n]", context) if part.strip()]
    return parts[:3]


def _display_emotion(emotion_code: str, language: str) -> str:
    return EMOTION_DISPLAY.get(emotion_code, EMOTION_DISPLAY["steady"]).get(language, emotion_code)


def _display_growth_signal(signal_code: str, language: str) -> str:
    return GROWTH_SIGNAL_DISPLAY.get(signal_code, GROWTH_SIGNAL_DISPLAY["consistency"]).get(language, signal_code)


def _style_cta(style_name: str, language: str) -> str:
    if language == "zh":
        return {
            "Storyteller": "这种小瞬间，也值得认真记一下。",
            "Warm Diary": "把今天的好心情留在这里。",
            "Playful Lifestyle": "生活感，有时候就是最好的内容感。",
            "Growth Reflection": "原来真正会留下来的，是这些慢慢积累的小变化。",
        }[style_name]
    return STYLE_LIBRARY[style_name]["cta"]


def _asset_role(index: int, total: int, language: str) -> str:
    if total <= 1:
        return "主画面" if language == "zh" else "hero shot"
    if index == 0:
        return "开场镜头" if language == "zh" else "opening shot"
    if index == total - 1:
        return "收尾镜头" if language == "zh" else "closing shot"
    return "细节镜头" if language == "zh" else "detail shot"


def _brightness_label(brightness: float, language: str) -> str:
    if language == "zh":
        if brightness > 185:
            return "偏亮"
        if brightness > 120:
            return "适中"
        return "偏暗"

    if brightness > 185:
        return "bright"
    if brightness > 120:
        return "balanced"
    return "dim"


def _palette_label_for_language(mean_rgb: Sequence[float], language: str) -> str:
    red, green, blue = mean_rgb
    brightness = (red + green + blue) / 3
    if language == "zh":
        light_label = "明快" if brightness > 185 else "柔和" if brightness > 120 else "沉静"
        if red - blue > 20:
            temp_label = "偏暖"
        elif blue - red > 20:
            temp_label = "偏冷"
        else:
            temp_label = "中性"
        return f"{light_label}、{temp_label}"

    light_label = "bright" if brightness > 185 else "balanced" if brightness > 120 else "moody"
    if red - blue > 20:
        temp_label = "warm"
    elif blue - red > 20:
        temp_label = "cool"
    else:
        temp_label = "neutral"
    return f"{light_label}, {temp_label}"


def _subject_hint(title: str, context: str, original_name: str, language: str) -> str:
    if language == "zh":
        clauses = _extract_chinese_phrases(f"{title}，{context}")
        if clauses:
            return _clip(clauses[0], 20)
        return "这次的小细节"

    tokens = []
    for token in _tokenize(f"{title} {context}"):
        cleaned = _clean_token(token)
        if cleaned:
            tokens.append(cleaned)
    if tokens:
        return " ".join(tokens[:3])

    filename_tokens = _meaningful_filename_tokens(original_name)
    if filename_tokens:
        return ", ".join(filename_tokens)
    return "everyday details"


def _normalize_title(title: str, context: str, language: str) -> str:
    normalized = title.strip()
    if normalized and normalized.lower() != "untitled moment":
        return normalized
    clauses = _extract_context_clauses(context, language)
    if clauses:
        return _clip(clauses[0], 24 if language == "zh" else 40)
    return DEFAULT_TITLE_BY_LANGUAGE[language]


def _sorted_style_weights(style_weights: Dict[str, float]) -> List[Tuple[str, float]]:
    merged = {**DEFAULT_STYLE_WEIGHTS, **style_weights}
    return sorted(merged.items(), key=lambda item: item[1], reverse=True)


def _profile_payload(profile: UserPreference) -> Dict[str, Any]:
    style_weights = _load_json(profile.style_weights_json, DEFAULT_STYLE_WEIGHTS.copy())
    top_tags = _load_json(profile.top_tags_json, [])
    voice_notes = _load_json(profile.voice_notes_json, [])
    exemplar_quotes = _load_json(profile.exemplar_quotes_json, [])
    top_styles = [name for name, _ in _sorted_style_weights(style_weights)[:3]]
    return {
        "preference_id": str(profile.preference_id),
        "user_id": str(profile.user_id),
        "style_weights": style_weights,
        "top_styles": top_styles,
        "top_tags": top_tags,
        "voice_notes": voice_notes,
        "exemplar_quotes": exemplar_quotes,
        "summary": profile.summary,
    }


def _refresh_profile_summary(profile_data: Dict[str, Any]) -> str:
    style_names = ", ".join(profile_data["top_styles"]) or "balanced social writing"
    tag_names = ", ".join(profile_data["top_tags"][:4]) or "still learning from the first few interactions"
    voice_notes = "; ".join(profile_data["voice_notes"][:2]) or "prefer grounded, human wording"
    return (
        f"Voice leans toward {style_names}. Current feedback says: {tag_names}. "
        f"Prompt memory note: {voice_notes}."
    )


def ensure_profile(db: Session, user_id: uuid.UUID) -> UserPreference:
    profile = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if profile:
        return profile

    profile_data = {
        "style_weights": DEFAULT_STYLE_WEIGHTS.copy(),
        "top_styles": [name for name, _ in _sorted_style_weights(DEFAULT_STYLE_WEIGHTS)[:3]],
        "top_tags": [],
        "voice_notes": [
            "Prefer concrete details over abstract filler.",
            "Keep posts warm and easy to publish without heavy edits.",
        ],
        "exemplar_quotes": [],
    }
    profile = UserPreference(
        user_id=user_id,
        style_weights_json=_dump_json(profile_data["style_weights"]),
        top_tags_json=_dump_json(profile_data["top_tags"]),
        voice_notes_json=_dump_json(profile_data["voice_notes"]),
        exemplar_quotes_json=_dump_json(profile_data["exemplar_quotes"]),
        summary=_refresh_profile_summary(profile_data),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def bootstrap_user(db: Session, user_id: Optional[str], username: Optional[str]) -> Tuple[User, UserPreference]:
    existing_user = None
    parsed_user_id = None
    if user_id:
        try:
            parsed_user_id = uuid.UUID(str(user_id))
        except ValueError as exc:
            raise ValueError("Invalid user_id format.") from exc
        existing_user = db.query(User).filter(User.user_id == parsed_user_id).first()

    if existing_user:
        return existing_user, ensure_profile(db, existing_user.user_id)

    display_name = (username or "Creator").strip() or "Creator"
    new_user = User(
        user_id=parsed_user_id or uuid.uuid4(),
        username=display_name,
        email=f"mvp-{uuid.uuid4().hex[:12]}@local.snaptale",
        password_hash="local-only",
        bio="MVP user for adaptive storytelling.",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, ensure_profile(db, new_user.user_id)


def _store_upload_file(
    upload_file: UploadFile,
    user_id: uuid.UUID,
    collection_id: uuid.UUID,
    backend_base_url: str,
) -> Tuple[Path, str]:
    suffix = Path(upload_file.filename or "image.jpg").suffix or ".jpg"
    destination_dir = UPLOAD_ROOT / str(user_id) / str(collection_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{uuid.uuid4().hex}{suffix.lower()}"

    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()

    relative_path = destination.relative_to(MEDIA_ROOT).as_posix()
    public_url = f"{backend_base_url.rstrip('/')}/media/{relative_path}"
    return destination, public_url


def _detect_emotion(text: str, fallback: str) -> str:
    tokens = set(_tokenize(text))
    if tokens & POSITIVE_HINTS:
        return "uplifting"
    if tokens & REFLECTIVE_HINTS:
        return "reflective"
    return fallback


def analyze_image(
    file_path: Path,
    original_name: str,
    title: str,
    context: str,
    language: str,
    index: int,
    total: int,
) -> Dict[str, Any]:
    try:
        with Image.open(file_path) as image:
            rgb_image = image.convert("RGB")
            width, height = rgb_image.size
            stat = ImageStat.Stat(rgb_image.resize((64, 64)))
            mean_rgb = stat.mean[:3]
    except Exception as exc:
        raise ValueError(f"{original_name} is not a readable image.") from exc

    orientation = "portrait" if height >= width else "landscape"
    brightness = round(sum(mean_rgb) / 3, 1)
    role = _asset_role(index, total, language)
    palette = _palette_label_for_language(mean_rgb, language)
    brightness_label = _brightness_label(brightness, language)
    filename_tokens = _meaningful_filename_tokens(original_name)
    keyword_hint = _subject_hint(title, context, original_name, language)
    mood_seed = "uplifting" if brightness > 165 else "reflective" if brightness < 110 else "steady"
    mood_tag = _detect_emotion(f"{title} {context} {keyword_hint}", mood_seed)
    emotion_display = _display_emotion(mood_tag, language)

    if language == "zh":
        analysis_text = (
            f"这张图更像{role}，画面{palette}，整体亮度{brightness_label}。"
            f"它主要在补充“{keyword_hint}”这个信息点，情绪上偏{emotion_display}。"
        )
    else:
        analysis_text = (
            f"This image works like a {role} with a {palette} palette and {brightness_label} light. "
            f"It reinforces the idea of {keyword_hint} and feels {emotion_display}."
        )

    metadata = {
        "width": width,
        "height": height,
        "orientation": orientation,
        "brightness": brightness,
        "palette": palette,
        "filename_tokens": filename_tokens,
        "role": role,
        "subject_hint": keyword_hint,
        "brightness_label": brightness_label,
    }
    return {
        "analysis_text": analysis_text,
        "mood_tag": mood_tag,
        "metadata": metadata,
    }


def _normalize_mood_tag(mood_tag: str, fallback: str) -> str:
    normalized = (mood_tag or "").strip().lower()
    if normalized in VALID_MOOD_TAGS:
        return normalized
    return fallback


def _memory_tokens(memory: MemoryItem) -> set:
    keywords = _load_json(memory.keywords_json, [])
    return set(_tokenize(" ".join([memory.title, memory.summary, memory.content, memory.emotion, memory.growth_signal, *keywords])))


def retrieve_memories(db: Session, user_id: uuid.UUID, query_text: str, limit: int = 3) -> List[MemoryItem]:
    memories = db.query(MemoryItem).filter(MemoryItem.user_id == user_id).all()
    if not memories:
        return []

    query_tokens = set(_tokenize(query_text))
    now = datetime.utcnow()
    scored_memories = []
    for memory in memories:
        overlap = len(query_tokens & _memory_tokens(memory))
        age_days = max((now - memory.created_at).days, 0)
        recency_bonus = max(0, 30 - age_days) / 30
        score = overlap * 2 + memory.strength + recency_bonus
        scored_memories.append((score, memory))

    scored_memories.sort(key=lambda item: item[0], reverse=True)
    return [memory for score, memory in scored_memories[:limit] if score > 0] or [memory for _, memory in scored_memories[:limit]]


def _pick_growth_signal(context: str, theme: str, emotion: str) -> str:
    combined = " ".join([context.lower(), theme.lower(), emotion.lower()])
    if any(token in combined for token in ["learn", "build", "habit", "practice", "training"]):
        return "skill-building"
    if any(token in combined for token in ["friend", "family", "team", "together"]):
        return "connection"
    if any(token in combined for token in ["travel", "new", "explore", "trip", "road"]):
        return "exploration"
    if any(token in combined for token in ["heal", "calm", "reset", "quiet"]):
        return "self-regulation"
    if any(token in combined for token in ["gift", "coffee", "treat", "surprise", "买", "礼品", "礼物", "咖啡", "开心", "联名"]):
        return "small-joy"
    return "consistency"


def _theme_candidates(title: str, context: str, assets: Sequence[Dict[str, Any]], language: str) -> List[str]:
    counter = Counter()
    if language == "zh":
        counter.update(phrase for phrase in _extract_chinese_phrases(f"{title}，{context}") if phrase not in GENERIC_CHINESE_TOKENS)
    else:
        counter.update(
            cleaned
            for token in _tokenize(f"{title} {context}")
            for cleaned in [_clean_token(token)]
            if cleaned
        )
    for asset in assets:
        metadata = asset["metadata"]
        counter.update(metadata.get("filename_tokens", []))
        subject_hint = metadata.get("subject_hint")
        if subject_hint:
            counter.update([subject_hint])
    if language == "zh":
        filtered = [token for token, _ in counter.most_common() if token and token not in GENERIC_CHINESE_TOKENS]
        return filtered[:5] or ["这组日常片段"]

    filtered = [token for token, _ in counter.most_common() if len(token) > 2]
    return filtered[:5] or ["moments", "story", "growth"]


def build_story(
    title: str,
    context: str,
    assets: Sequence[Dict[str, Any]],
    retrieved_memories: Sequence[MemoryItem],
    profile: UserPreference,
) -> Dict[str, Any]:
    language = _detect_language(title, context)
    normalized_title = _normalize_title(title, context, language)
    themes = _theme_candidates(normalized_title, context, assets, language)
    main_theme = normalized_title if normalized_title else themes[0].replace("-", " ")
    mood_counter = Counter(asset["mood_tag"] for asset in assets)
    emotional_tone_code = mood_counter.most_common(1)[0][0]
    emotional_tone = _display_emotion(emotional_tone_code, language)
    growth_signal_code = _pick_growth_signal(context, main_theme, emotional_tone_code)
    growth_signal = _display_growth_signal(growth_signal_code, language)
    context_clauses = _extract_context_clauses(context, language)
    opening_role = assets[0]["metadata"].get("role", "opening shot")
    closing_role = assets[-1]["metadata"].get("role", "closing shot")
    subject_hints = [asset["metadata"].get("subject_hint", "") for asset in assets if asset["metadata"].get("subject_hint", "")]
    detail_hint = subject_hints[0] if subject_hints else (themes[1] if len(themes) > 1 else main_theme)
    memory_hint = retrieved_memories[0].summary if retrieved_memories else ""

    if language == "zh":
        story_summary = f"这组照片围绕“{main_theme}”展开，整体氛围偏{emotional_tone}。"
        if context_clauses:
            story_summary += f" 从你的描述来看，重点是{context_clauses[0]}。"
        story_summary += f" 画面先用{opening_role}交代场景，再把注意力落到“{detail_hint}”这样的细节上，最后由{closing_role}把这次记录收住。"
        if memory_hint:
            story_summary += f" 它也和你之前记录过的状态形成了呼应：{_clip(memory_hint, 40)}。"

        narrative_arc = (
            f"开头先把主题亮出来，中段放大你最在意的细节，结尾把这次经历落成一个适合分享的{growth_signal}片段。"
        )
    else:
        story_summary = f"This collection revolves around {main_theme} with a mostly {emotional_tone} tone."
        if context_clauses:
            story_summary += f" From the user's note, the key point is {context_clauses[0]}."
        story_summary += (
            f" It opens with an {opening_role}, moves toward details like {detail_hint}, "
            f"and lets the {closing_role} land the ending."
        )
        if memory_hint:
            story_summary += f" It also echoes an earlier memory: {_clip(memory_hint, 90)}."

        narrative_arc = (
            f"Start by naming the moment, spend the middle on the most human detail, "
            f"and end by turning it into a shareable {growth_signal} update."
        )

    profile_notes = _profile_payload(profile)
    return {
        "title": normalized_title or f"{main_theme.title()} Update",
        "story_summary": story_summary,
        "narrative_arc": narrative_arc,
        "emotional_tone": emotional_tone,
        "main_theme": main_theme,
        "themes": themes,
        "growth_signal": growth_signal,
        "language": language,
        "context_clauses": context_clauses,
        "profile_notes": profile_notes,
    }


def _hashtags(story: Dict[str, Any], style_name: str) -> str:
    language = story.get("language", "en")
    style_tag = STYLE_LABEL_ZH.get(style_name, style_name) if language == "zh" else style_name.lower()
    raw_tags = [story["main_theme"], story["growth_signal"], story["emotional_tone"], style_tag]
    tags = []
    for raw in raw_tags:
        if language == "zh":
            cleaned = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", raw)
        else:
            cleaned = "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", raw) if part)
        if cleaned:
            tags.append(f"#{cleaned}")
    return " ".join(tags[:4])


def _render_post(style_name: str, story: Dict[str, Any], retrieved_memories: Sequence[MemoryItem]) -> Dict[str, str]:
    style_meta = STYLE_LIBRARY[style_name]
    language = story.get("language", "en")
    context_clauses = story.get("context_clauses", [])
    memory_line = ""
    if retrieved_memories:
        if language == "zh":
            memory_line = f" 也会让我想到你之前记录过的“{retrieved_memories[0].title}”。"
        else:
            memory_line = f" It also echoes an earlier chapter about {retrieved_memories[0].title.lower()}."

    if language == "zh":
        base_context = context_clauses[0] if context_clauses else f"这次关于“{story['main_theme']}”的小记录"
        hook = {
            "Storyteller": f"本来只是随手记录一下，结果这组图把“{story['main_theme']}”讲得很完整。",
            "Warm Diary": f"我很喜欢这种不需要刻意安排、但会让人想记下来的时刻。",
            "Playful Lifestyle": f"有时候让人开心的，不是大事，就是这种刚刚好的小惊喜。",
            "Growth Reflection": f"把这些画面放在一起，会发现生活里的满足感其实有迹可循。",
        }[style_name]

        body = {
            "Storyteller": (
                f"{hook} {base_context}。整组照片的节奏很自然，先把场景交代清楚，再把注意力放到细节和情绪上。"
                f" 最后留下来的，不只是一次消费记录，更像是一个会想分享给朋友看的小片段。{memory_line}"
            ),
            "Warm Diary": (
                f"{hook} {base_context}。我喜欢它带来的那种{story['emotional_tone']}感觉，"
                f" 不是特别用力，但会让人真切地记住当下。{memory_line}"
            ),
            "Playful Lifestyle": (
                f"{hook} {base_context}。咖啡、包装、礼物这些细节凑在一起，刚好把今天的小快乐拼完整了。"
                f" 这种照片最适合发出来，因为看起来轻松，背后又有点自己的趣味。{memory_line}"
            ),
            "Growth Reflection": (
                f"{hook} {base_context}。比起“发生了什么”，我更在意这组图提醒了我什么："
                f" 原来生活感和分享欲，真的可以被这种{story['growth_signal']}瞬间慢慢积累出来。{memory_line}"
            ),
        }[style_name]
    else:
        base_context = context_clauses[0] if context_clauses else f"a small update about {story['main_theme']}"
        hook = {
            "Storyteller": f"A quick camera-roll post ended up telling a fuller story about {story['main_theme']}.",
            "Warm Diary": f"I'm drawn to the kind of moment that feels small but still worth keeping.",
            "Playful Lifestyle": f"Sometimes the best content is just a tiny, unexpectedly satisfying slice of life.",
            "Growth Reflection": f"Lining these frames up makes the emotional pattern easier to see.",
        }[style_name]

        body = {
            "Storyteller": (
                f"{hook} {base_context}. The sequence moves naturally from scene-setting into detail, "
                f"so it reads less like a dump and more like a lived moment.{memory_line}"
            ),
            "Warm Diary": (
                f"{hook} {base_context}. What I want to keep is the {story['emotional_tone']} feeling of it all: "
                f"simple, specific, and easy to recognize later.{memory_line}"
            ),
            "Playful Lifestyle": (
                f"{hook} {base_context}. The details are the real payoff here, and they make the whole thing feel polished "
                f"without losing the personal edge.{memory_line}"
            ),
            "Growth Reflection": (
                f"{hook} {base_context}. What stays with me most is the sense of {story['growth_signal']}: "
                f"small moments adding up to a clearer personal rhythm.{memory_line}"
            ),
        }[style_name]

    closing = f"{_style_cta(style_name, language)} {_hashtags(story, style_name)}"
    return {"hook": hook, "content": f"{body}\n\n{closing}"}


def _serialize_collection(collection: PhotoCollection) -> Dict[str, Any]:
    return {
        "collection_id": str(collection.collection_id),
        "user_id": str(collection.user_id),
        "title": collection.title,
        "context": collection.context,
        "story_summary": collection.story_summary,
        "narrative_arc": collection.narrative_arc,
        "emotional_tone": collection.emotional_tone,
        "created_at": collection.created_at.isoformat(),
        "updated_at": collection.updated_at.isoformat(),
    }


def _serialize_asset(asset: CollectionAsset) -> Dict[str, Any]:
    return {
        "asset_id": str(asset.asset_id),
        "collection_id": str(asset.collection_id),
        "file_name": asset.file_name,
        "public_url": asset.public_url,
        "analysis_text": asset.analysis_text,
        "mood_tag": asset.mood_tag,
        "metadata": _load_json(asset.metadata_json, {}),
        "created_at": asset.created_at.isoformat(),
    }


def _serialize_post(post: GeneratedPost) -> Dict[str, Any]:
    return {
        "post_id": str(post.post_id),
        "collection_id": str(post.collection_id),
        "style_name": post.style_name,
        "hook": post.hook,
        "content": post.content,
        "is_selected": post.is_selected,
        "created_at": post.created_at.isoformat(),
    }


def _serialize_memory(memory: MemoryItem) -> Dict[str, Any]:
    return {
        "memory_id": str(memory.memory_id),
        "collection_id": str(memory.collection_id) if memory.collection_id else None,
        "source_type": memory.source_type,
        "title": memory.title,
        "summary": memory.summary,
        "emotion": memory.emotion,
        "growth_signal": memory.growth_signal,
        "content": memory.content,
        "keywords": _load_json(memory.keywords_json, []),
        "strength": memory.strength,
        "created_at": memory.created_at.isoformat(),
    }


def generate_collection_content(
    db: Session,
    user: User,
    profile: UserPreference,
    title: str,
    context: str,
    files: Sequence[UploadFile],
    backend_base_url: str,
) -> Dict[str, Any]:
    if not files:
        raise ValueError("Please upload at least one photo.")

    config = get_model_config()
    language = _detect_language(title, context)
    normalized_title = _normalize_title(title, context, language)
    collection = PhotoCollection(
        user_id=user.user_id,
        title=normalized_title,
        context=context.strip(),
    )
    db.add(collection)

    stored_assets: List[CollectionAsset] = []
    asset_snapshots: List[Dict[str, Any]] = []
    provider_notes: List[str] = []
    image_llm_used_count = 0
    query_seed = " ".join([collection.title, collection.context, " ".join(upload.filename or "" for upload in files)])
    retrieved_memories = retrieve_memories(db, user.user_id, query_seed)
    profile_data = _profile_payload(profile)

    total_files = len(files)
    for index, upload in enumerate(files):
        file_path, public_url = _store_upload_file(upload, user.user_id, collection.collection_id, backend_base_url)
        analysis = analyze_image(
            file_path=file_path,
            original_name=upload.filename or file_path.name,
            title=collection.title,
            context=context,
            language=language,
            index=index,
            total=total_files,
        )
        if config.use_llm:
            try:
                llm_analysis = analyze_image_with_llm(
                    config,
                    file_path=file_path,
                    title=collection.title,
                    context=context,
                    language=language,
                    role_label=analysis["metadata"].get("role", ""),
                )
                if llm_analysis.get("analysis_text"):
                    analysis["analysis_text"] = llm_analysis["analysis_text"]
                analysis["mood_tag"] = _normalize_mood_tag(llm_analysis.get("mood_tag", ""), analysis["mood_tag"])
                if llm_analysis.get("subject_hint"):
                    analysis["metadata"]["subject_hint"] = llm_analysis["subject_hint"]
                analysis["metadata"]["analysis_source"] = "llm"
                image_llm_used_count += 1
            except ModelProviderError as exc:
                analysis["metadata"]["analysis_source"] = "heuristic"
                provider_notes.append(
                    f"Image analysis fell back for '{upload.filename or file_path.name}': {exc}"
                )
        else:
            analysis["metadata"]["analysis_source"] = "heuristic"

        asset = CollectionAsset(
            collection_id=collection.collection_id,
            user_id=user.user_id,
            file_name=upload.filename or file_path.name,
            file_path=str(file_path),
            public_url=public_url,
            analysis_text=analysis["analysis_text"],
            mood_tag=analysis["mood_tag"],
            metadata_json=_dump_json(analysis["metadata"]),
        )
        db.add(asset)
        stored_assets.append(asset)
        asset_snapshots.append(
            {
                "file_name": upload.filename or file_path.name,
                "public_url": public_url,
                "analysis_text": analysis["analysis_text"],
                "mood_tag": analysis["mood_tag"],
                "metadata": analysis["metadata"],
            }
        )

    story = build_story(collection.title, collection.context, asset_snapshots, retrieved_memories, profile)
    llm_posts_by_style: Dict[str, Dict[str, str]] = {}
    story_generation_mode = "heuristic"
    if config.use_llm:
        try:
            llm_story = generate_story_with_llm(
                config,
                language=story["language"],
                title=collection.title,
                context=collection.context,
                profile=profile_data,
                retrieved_memories=[_serialize_memory(memory) for memory in retrieved_memories],
                asset_briefs=asset_snapshots,
                fallback_story=story,
            )
            story.update(
                {
                    "story_summary": llm_story["story_summary"],
                    "narrative_arc": llm_story["narrative_arc"],
                    "emotional_tone": llm_story["emotional_tone"],
                    "growth_signal": llm_story["growth_signal"],
                    "themes": llm_story["themes"],
                }
            )
            llm_posts_by_style = {
                post["style_name"]: {
                    "hook": post["hook"],
                    "content": post["content"],
                }
                for post in llm_story["posts"]
            }
            story_generation_mode = "llm"
        except ModelProviderError as exc:
            provider_notes.append(f"Story generation fell back to heuristic drafting: {exc}")

    collection.story_summary = story["story_summary"]
    collection.narrative_arc = story["narrative_arc"]
    collection.emotional_tone = story["emotional_tone"]
    collection.retrieved_memory_ids_json = _dump_json([str(memory.memory_id) for memory in retrieved_memories])

    image_analysis_mode = "llm" if image_llm_used_count == total_files else "mixed" if image_llm_used_count else "heuristic"
    response_generation_info = generation_info(
        config,
        {
            "image_analysis_mode": image_analysis_mode,
            "image_llm_used_count": image_llm_used_count,
            "image_total_count": total_files,
            "story_generation_mode": story_generation_mode,
            "provider_notes": provider_notes[:8],
        },
    )
    post_rows: List[GeneratedPost] = []
    for style_name, _ in _sorted_style_weights(profile_data["style_weights"]):
        rendered = llm_posts_by_style.get(style_name) or _render_post(style_name, story, retrieved_memories)
        post = GeneratedPost(
            collection_id=collection.collection_id,
            user_id=user.user_id,
            style_name=style_name,
            hook=rendered["hook"],
            content=rendered["content"],
            prompt_snapshot=_dump_json(
                {
                    "style": style_name,
                    "profile": profile_data,
                    "retrieved_memories": [_serialize_memory(memory) for memory in retrieved_memories],
                    "story": story,
                    "generation_info": response_generation_info,
                }
            ),
        )
        db.add(post)
        post_rows.append(post)

    memory = MemoryItem(
        user_id=user.user_id,
        collection_id=collection.collection_id,
        source_type="collection_story",
        title=story["title"],
        summary=_clip(story["story_summary"], 260),
        emotion=story["emotional_tone"],
        growth_signal=story["growth_signal"],
        content=f"{story['story_summary']} {story['narrative_arc']}",
        keywords_json=_dump_json(story["themes"]),
        strength=1.2 if retrieved_memories else 1.0,
    )
    db.add(memory)
    db.commit()
    db.refresh(collection)
    for asset in stored_assets:
        db.refresh(asset)
    for post in post_rows:
        db.refresh(post)
    db.refresh(memory)

    return {
        "collection": _serialize_collection(collection),
        "assets": [_serialize_asset(asset) for asset in stored_assets],
        "posts": [_serialize_post(post) for post in post_rows],
        "retrieved_memories": [_serialize_memory(item) for item in retrieved_memories],
        "profile": _profile_payload(profile),
        "memory": _serialize_memory(memory),
        "generation_info": response_generation_info,
    }


def _merge_top_tags(existing_tags: Sequence[str], new_tags: Sequence[str], style_name: str, signal_type: str) -> List[str]:
    counter = Counter(existing_tags)
    counter.update(tag.strip().lower() for tag in new_tags if tag and tag.strip())
    if signal_type == "select":
        counter.update([f"selected:{style_name.lower()}"])
    elif signal_type == "dislike":
        counter.update([f"avoid:{style_name.lower()}"])
    ordered = [tag for tag, _ in counter.most_common(8)]
    return ordered


def apply_feedback(
    db: Session,
    user_id: uuid.UUID,
    post_id: uuid.UUID,
    signal_type: str,
    rating: Optional[int],
    tags: Sequence[str],
    rewrite_text: str,
) -> Dict[str, Any]:
    post = db.query(GeneratedPost).filter(GeneratedPost.post_id == post_id, GeneratedPost.user_id == user_id).first()
    if post is None:
        raise ValueError("Post not found.")

    profile = ensure_profile(db, user_id)
    feedback = FeedbackEvent(
        user_id=user_id,
        collection_id=post.collection_id,
        post_id=post.post_id,
        signal_type=signal_type,
        rating=rating,
        tags_json=_dump_json(list(tags)),
        rewrite_text=rewrite_text.strip(),
    )
    db.add(feedback)

    profile_data = _profile_payload(profile)
    style_weights = profile_data["style_weights"]
    top_tags = profile_data["top_tags"]
    voice_notes = profile_data["voice_notes"]
    exemplar_quotes = profile_data["exemplar_quotes"]

    delta = 0.0
    if signal_type in {"like", "select"}:
        delta = 0.35
    elif signal_type == "dislike":
        delta = -0.3
    elif signal_type == "rewrite":
        delta = 0.2
    if rating:
        delta += max(-2, min(2, rating)) * 0.05

    style_weights[post.style_name] = round(style_weights.get(post.style_name, 1.0) + delta, 2)
    style_weights[post.style_name] = max(0.1, min(2.5, style_weights[post.style_name]))

    merged_tags = _merge_top_tags(top_tags, tags, post.style_name, signal_type)
    if rewrite_text.strip():
        exemplar_quotes = [_clip(rewrite_text.strip(), 180), *exemplar_quotes][:4]
        voice_notes = [
            "User edits toward more specific, personally owned phrasing.",
            *voice_notes,
        ][:4]
    if signal_type == "dislike":
        voice_notes = [f"Reduce {post.style_name.lower()} phrasing unless explicitly requested.", *voice_notes][:4]
    elif signal_type == "select":
        voice_notes = [f"Lean into {post.style_name.lower()} structure for future drafts.", *voice_notes][:4]

    profile_data["style_weights"] = style_weights
    profile_data["top_tags"] = merged_tags
    profile_data["voice_notes"] = voice_notes[:4]
    profile_data["top_styles"] = [name for name, _ in _sorted_style_weights(style_weights)[:3]]
    profile_data["exemplar_quotes"] = exemplar_quotes
    profile.summary = _refresh_profile_summary(profile_data)
    profile.style_weights_json = _dump_json(style_weights)
    profile.top_tags_json = _dump_json(merged_tags)
    profile.voice_notes_json = _dump_json(profile_data["voice_notes"])
    profile.exemplar_quotes_json = _dump_json(exemplar_quotes)

    if signal_type == "select":
        sibling_posts = db.query(GeneratedPost).filter(GeneratedPost.collection_id == post.collection_id).all()
        for sibling in sibling_posts:
            sibling.is_selected = sibling.post_id == post.post_id

    preference_memory = MemoryItem(
        user_id=user_id,
        collection_id=post.collection_id,
        source_type="feedback",
        title=f"{post.style_name} feedback",
        summary=f"User gave a {signal_type} signal to the {post.style_name} draft.",
        emotion="preference",
        growth_signal="voice-tuning",
        content=rewrite_text.strip() or "No rewrite text supplied.",
        keywords_json=_dump_json([post.style_name, signal_type, *list(tags)]),
        strength=0.8,
    )
    db.add(preference_memory)
    db.commit()
    db.refresh(profile)
    db.refresh(post)
    db.refresh(preference_memory)

    collection_posts = (
        db.query(GeneratedPost)
        .filter(GeneratedPost.collection_id == post.collection_id)
        .order_by(GeneratedPost.created_at.asc())
        .all()
    )
    return {
        "profile": _profile_payload(profile),
        "posts": [_serialize_post(item) for item in collection_posts],
        "memory": _serialize_memory(preference_memory),
    }


def get_growth_view(db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise ValueError("User not found.")

    profile = ensure_profile(db, user_id)
    memories = db.query(MemoryItem).filter(MemoryItem.user_id == user_id).order_by(MemoryItem.created_at.desc()).all()
    collections = db.query(PhotoCollection).filter(PhotoCollection.user_id == user_id).order_by(PhotoCollection.created_at.desc()).all()
    feedback_count = db.query(FeedbackEvent).filter(FeedbackEvent.user_id == user_id).count()

    emotion_counter = Counter(memory.emotion for memory in memories)
    growth_counter = Counter(memory.growth_signal for memory in memories)

    return {
        "user": {
            "user_id": str(user.user_id),
            "username": user.username,
        },
        "profile": _profile_payload(profile),
        "stats": {
            "collection_count": len(collections),
            "memory_count": len(memories),
            "feedback_count": feedback_count,
            "top_emotion": emotion_counter.most_common(1)[0][0] if emotion_counter else "steady",
            "top_growth_signal": growth_counter.most_common(1)[0][0] if growth_counter else "consistency",
        },
        "timeline": [_serialize_memory(memory) for memory in memories[:20]],
        "collections": [_serialize_collection(collection) for collection in collections[:12]],
    }
