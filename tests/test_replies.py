from datetime import date

from agent.contract import NotProduce, Produce
from agent.excel_log import DailyCounts
from agent.replies import error_reply, not_produce_reply, photo_label, produce_reply

COUNTS = DailyCounts(date(2026, 10, 26), 7, 4, 3)


def banana(**changes):
    values = dict(produce_type="fruit", name="Banana", freshness_score=72, ready_to_eat="yes",
                  days_left=2, storage_tip="Keep at room temperature, away from other fruit.",
                  confidence=88, description="Mostly yellow with a few brown spots, skin looks slightly soft.")
    return Produce(**{**values, **changes})


def test_produce_reply_matches_architecture():
    assert produce_reply(banana(), COUNTS) == (
        "🍎 Banana (fruit)\n"
        "Freshness: 72/100 — Ready to eat: ✅ Yes\n"
        "Good for about 2 more days\n"
        "Mostly yellow with a few brown spots, skin looks slightly soft.\n"
        "Tip: Keep at room temperature, away from other fruit.\n"
        "Confidence: High\n"
        "Today: 7 checked (4 fruits, 3 vegetables)"
    )


def test_low_confidence_vegetable_with_label():
    text = produce_reply(banana(produce_type="vegetable", name="Carrot", ready_to_eat="past_best",
                                days_left=0, confidence=49), COUNTS, photo_label(2, 3))
    lines = text.splitlines()
    assert lines[0] == "Photo 2 of 3"
    assert lines[1] == "🥕 Carrot (vegetable)"
    assert "⚠️ Past its best" in lines[2]
    assert lines[3] == "Best used today"
    assert lines[-3:] == ["Confidence: Low", "🔍 Low confidence — a clearer, well-lit photo would help",
                          "Today: 7 checked (4 fruits, 3 vegetables)"]


def test_medium_confidence_and_not_yet():
    text = produce_reply(banana(ready_to_eat="not_yet", days_left=1, confidence=50), COUNTS)
    assert "🟡 Not yet" in text and "Good for about 1 more day" in text
    assert "Confidence: Medium" in text and "🔍" not in text


def test_not_produce_and_error_replies():
    assert not_produce_reply(NotProduce(95, "a cat."), COUNTS) == (
        "This doesn't look like a fruit or vegetable — I see a cat.\n"
        "Today: 7 checked (4 fruits, 3 vegetables)"
    )
    assert error_reply(COUNTS) == (
        "Recognition failed, please send the photo again\nToday: 7 checked (4 fruits, 3 vegetables)"
    )
    assert photo_label(1, 1) == ""
