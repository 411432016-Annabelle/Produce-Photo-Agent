import json

import pytest

from agent.contract import ContractError, NotProduce, Produce, parse_claude_output
from tests.helpers import BANANA, CAT, envelope


def with_changes(**changes):
    return {**BANANA, **changes}


def test_valid_produce():
    result = parse_claude_output(envelope(BANANA))
    assert result == Produce("fruit", "Banana", 72, "yes", 2, "Keep at room temperature.", 88,
                             "Mostly yellow with a few brown spots.")


def test_valid_not_produce():
    assert parse_claude_output(envelope(CAT)) == NotProduce(confidence=95, description="a cat")


def test_code_fences_are_accepted():
    fenced = "```json\n" + json.dumps(BANANA) + "\n```"
    assert isinstance(parse_claude_output(envelope(fenced)), Produce)


def test_numbers_are_rounded():
    result = parse_claude_output(envelope(with_changes(freshness_score=71.6, days_left=2.0)))
    assert (result.freshness_score, result.days_left) == (72, 2)


@pytest.mark.parametrize("stdout, reason", [
    ("not json at all", "claude -p output was not valid JSON"),
    (json.dumps({"is_error": True, "result": "usage limit reached"}), "claude -p reported an error"),
    (envelope("Sure! Here is my answer."), "answer was not valid JSON"),
    (envelope("[1, 2]"), "answer was not a JSON object"),
    (envelope(with_changes(is_produce="yes")), "is_produce is not true/false"),
    (envelope(with_changes(freshness_score="seventy")), "freshness_score is not a number"),
    (envelope(with_changes(freshness_score=True)), "freshness_score is not a number"),
    (envelope(with_changes(freshness_score=101)), "freshness_score is outside 0-100"),
    (envelope(with_changes(confidence=None)), "confidence is not a number"),
    (envelope(with_changes(days_left=2.5)), "days_left is not a whole number"),
    (envelope(with_changes(days_left=-1)), "days_left is outside 0-365"),
    (envelope(with_changes(ready_to_eat="ripe")), "ready_to_eat is not yes/not_yet/past_best"),
    (envelope(with_changes(produce_type="nut")), "produce_type is not fruit/vegetable"),
    (envelope(with_changes(name="")), "name is missing or not text"),
    (envelope(with_changes(name="x" * 41)), "name is longer than 40 characters"),
    (envelope({k: v for k, v in BANANA.items() if k != "storage_tip"}), "storage_tip is missing or not text"),
])
def test_invalid_answers_are_rejected(stdout, reason):
    with pytest.raises(ContractError) as error:
        parse_claude_output(stdout)
    assert str(error.value).startswith(reason)
