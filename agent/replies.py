"""Reply text (architecture section 10)."""

from .contract import NotProduce, Produce
from .excel_log import DailyCounts

READY_LABELS = {"yes": "✅ Yes", "not_yet": "🟡 Not yet", "past_best": "⚠️ Past its best"}
TYPE_EMOJI = {"fruit": "🍎", "vegetable": "🥕"}
HIGH_CONFIDENCE = 80
LOW_CONFIDENCE = 50
FAILED_TEXT = "Recognition failed, please send the photo again"


def confidence_label(confidence: int) -> str:
    if confidence >= HIGH_CONFIDENCE:
        return "High"
    if confidence >= LOW_CONFIDENCE:
        return "Medium"
    return "Low"


def days_text(days_left: int) -> str:
    if days_left == 0:
        return "Best used today"
    if days_left == 1:
        return "Good for about 1 more day"
    return f"Good for about {days_left} more days"


def today_line(counts: DailyCounts) -> str:
    return f"Today: {counts.total} checked ({counts.fruits} fruits, {counts.vegetables} vegetables)"


def produce_reply(result: Produce, counts: DailyCounts, photo_label: str = "") -> str:
    lines = [
        f"{TYPE_EMOJI[result.produce_type]} {result.name} ({result.produce_type})",
        f"Freshness: {result.freshness_score}/100 — Ready to eat: {READY_LABELS[result.ready_to_eat]}",
        days_text(result.days_left),
        result.description,
        f"Tip: {result.storage_tip}",
        f"Confidence: {confidence_label(result.confidence)}",
    ]
    if result.confidence < LOW_CONFIDENCE:
        lines.append("🔍 Low confidence — a clearer, well-lit photo would help")
    lines.append(today_line(counts))
    return _with_label(lines, photo_label)


def not_produce_reply(result: NotProduce, counts: DailyCounts, photo_label: str = "") -> str:
    lines = [
        f"This doesn't look like a fruit or vegetable — I see {result.description.rstrip(".")}.",
        today_line(counts),
    ]
    return _with_label(lines, photo_label)


def error_reply(counts: DailyCounts, photo_label: str = "") -> str:
    return _with_label([FAILED_TEXT, today_line(counts)], photo_label)


def photo_label(index: int, total: int) -> str:
    return f"Photo {index} of {total}" if total > 1 else ""


def _with_label(lines: list[str], label: str) -> str:
    return "\n".join([label, *lines] if label else lines)
