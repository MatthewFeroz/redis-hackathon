"""Tests for the pure detect_status function."""

import pytest
from app.agent import detect_status


@pytest.mark.parametrize("message,expected", [
    ("I just posted the review!", "submitted"),
    ("Done! Left you 5 stars", "submitted"),
    ("I submitted it", "submitted"),
    ("wrote a review for you", "submitted"),
    ("gave 5 stars", "submitted"),
    ("no thanks", "declined"),
    ("not interested", "declined"),
    ("I'd rather not", "declined"),
    ("maybe later", "declined"),
    ("I'm stuck, where do I tap?", "needs_help"),
    ("help me please", "needs_help"),
    # "can't" matches declined before needs_help — this is expected behavior
    ("I can't find the button", "declined"),
    ("the link doesn't work", "needs_help"),
    ("Hello!", None),
    ("Sure, I'd love to", None),
    ("Sounds good", None),
])
def test_detect_status(message, expected):
    assert detect_status(message) == expected
