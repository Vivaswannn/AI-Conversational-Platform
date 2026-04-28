import os
import pytest
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")

from app.services.crisis_service import CrisisDetector, CrisisSeverity


def test_no_crisis_in_normal_message():
    detector = CrisisDetector()
    result = detector.detect_keywords("I feel a bit stressed today about work")
    assert result == CrisisSeverity.NONE


def test_critical_keyword_detected():
    detector = CrisisDetector()
    result = detector.detect_keywords("I want to kill myself")
    assert result == CrisisSeverity.CRITICAL


def test_high_keyword_detected():
    detector = CrisisDetector()
    result = detector.detect_keywords("I've been thinking about self-harm")
    assert result == CrisisSeverity.HIGH


def test_medium_keyword_detected():
    detector = CrisisDetector()
    result = detector.detect_keywords("I feel completely hopeless")
    assert result == CrisisSeverity.MEDIUM


def test_low_keyword_detected():
    detector = CrisisDetector()
    result = detector.detect_keywords("I feel really sad and depressed")
    assert result == CrisisSeverity.LOW


def test_case_insensitive_detection():
    detector = CrisisDetector()
    result = detector.detect_keywords("I WANT TO END MY LIFE")
    assert result == CrisisSeverity.CRITICAL


def test_get_safety_response_critical():
    detector = CrisisDetector()
    response = detector.get_safety_response(CrisisSeverity.CRITICAL)
    assert "988" in response
    assert response  # not empty


def test_get_safety_response_none_returns_none():
    detector = CrisisDetector()
    response = detector.get_safety_response(CrisisSeverity.NONE)
    assert response is None
