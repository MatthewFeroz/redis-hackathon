"""Tests for the ChatTimer utility."""

import time
import pytest
from app.agent import ChatTimer


def test_timer_disabled_records_nothing():
    timer = ChatTimer(enabled=False)
    with timer.step("some_step"):
        time.sleep(0.001)
    assert timer.steps == {}


def test_timer_enabled_records_steps():
    timer = ChatTimer(enabled=True)
    with timer.step("fast_step"):
        time.sleep(0.01)
    with timer.step("another_step"):
        time.sleep(0.01)
    assert "fast_step" in timer.steps
    assert "another_step" in timer.steps
    assert timer.steps["fast_step"] > 0
    assert timer.steps["another_step"] > 0


def test_timer_total_ms():
    timer = ChatTimer(enabled=True)
    with timer.step("a"):
        time.sleep(0.01)
    with timer.step("b"):
        time.sleep(0.01)
    assert timer.total_ms >= timer.steps["a"] + timer.steps["b"] - 0.1
