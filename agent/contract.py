"""Parses and validates the claude -p answer (architecture section 5)."""

import json
import math
import re
from dataclasses import dataclass

READY_VALUES = {"yes": "Yes", "not_yet": "Not yet", "past_best": "Past its best"}
PRODUCE_TYPES = ("fruit", "vegetable")


class ContractError(Exception):
    """The answer broke the contract. The message is a short reason for the Error row."""


@dataclass(frozen=True)
class Produce:
    produce_type: str
    name: str
    freshness_score: int
    ready_to_eat: str  # "yes" / "not_yet" / "past_best"
    days_left: int
    storage_tip: str
    confidence: int
    description: str


@dataclass(frozen=True)
class NotProduce:
    confidence: int
    description: str


def parse_claude_output(stdout: str) -> Produce | NotProduce:
    """Turns the raw stdout of `claude -p --output-format json` into a checked result."""
    answer_text = _unwrap_envelope(stdout)
    data = _parse_answer_json(answer_text)

    is_produce = data.get("is_produce")
    if not isinstance(is_produce, bool):
        raise ContractError("is_produce is not true/false")

    confidence = _number(data, "confidence", 0, 100)
    description = _text(data, "description", 200)
    if not is_produce:
        return NotProduce(confidence=confidence, description=description)

    produce_type = data.get("produce_type")
    if produce_type not in PRODUCE_TYPES:
        raise ContractError("produce_type is not fruit/vegetable")
    ready_to_eat = data.get("ready_to_eat")
    if ready_to_eat not in READY_VALUES:
        raise ContractError("ready_to_eat is not yes/not_yet/past_best")

    return Produce(
        produce_type=produce_type,
        name=_text(data, "name", 40),
        freshness_score=_number(data, "freshness_score", 0, 100),
        ready_to_eat=ready_to_eat,
        days_left=_number(data, "days_left", 0, 365, whole=True),
        storage_tip=_text(data, "storage_tip", 200),
        confidence=confidence,
        description=description,
    )


def _unwrap_envelope(stdout: str) -> str:
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        raise ContractError("claude -p output was not valid JSON") from None
    if not isinstance(envelope, dict):
        raise ContractError("claude -p output was not a JSON object")
    if envelope.get("is_error"):
        raise ContractError(f"claude -p reported an error: {str(envelope.get('result', ''))[:120]}")
    result = envelope.get("result")
    if not isinstance(result, str):
        raise ContractError("claude -p output had no answer text")
    return result


def _parse_answer_json(text: str) -> dict:
    text = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ContractError("answer was not valid JSON") from None
    if not isinstance(data, dict):
        raise ContractError("answer was not a JSON object")
    return data


def _number(data: dict, field: str, low: int, high: int, whole: bool = False) -> int:
    value = data.get(field)
    # bool is a subclass of int in Python, so rule it out explicitly.
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{field} is not a number")
    if whole and value != int(value):
        raise ContractError(f"{field} is not a whole number")
    if not low <= value <= high:
        raise ContractError(f"{field} is outside {low}-{high}")
    return round(value)


def _text(data: dict, field: str, max_length: int) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} is missing or not text")
    value = " ".join(value.split())
    if len(value) > max_length:
        raise ContractError(f"{field} is longer than {max_length} characters")
    return value
