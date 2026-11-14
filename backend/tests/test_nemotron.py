from unittest.mock import MagicMock, patch

import pytest

from backend.services.nemotron import classify_post


def mock_response(content):
    response = MagicMock()
    response.choices[0].message.content = content
    return response


@patch("backend.services.nemotron.client")
def test_normal_post(mock_client):
    mock_client.chat.completions.create.return_value = mock_response(
        '{"techniques": [], "confidence": 0.0, '
        '"explanation": "No clear manipulation.", "evidence": []}'
    )

    result = classify_post("A normal social media post.")

    assert result["techniques"] == []
    assert result["confidence"] == 0.0


@patch("backend.services.nemotron.client")
def test_emotional_manipulation(mock_client):
    mock_client.chat.completions.create.return_value = mock_response(
        '{"techniques": ["emotional_manipulation"], '
        '"confidence": 0.8, '
        '"explanation": "Uses urgency and fear.", '
        '"evidence": ["SHARE THIS NOW!"]}'
    )

    result = classify_post("SHARE THIS NOW!")

    assert "emotional_manipulation" in result["techniques"]
    assert result["confidence"] == 0.8


@patch("backend.services.nemotron.client")
def test_empty_post(mock_client):
    result = classify_post("")

    assert result["techniques"] == []
    mock_client.chat.completions.create.assert_not_called()


@patch("backend.services.nemotron.client")
def test_invalid_technique(mock_client):
    mock_client.chat.completions.create.return_value = mock_response(
        '{"techniques": ["unknown_technique"], '
        '"confidence": 0.9, '
        '"explanation": "Invalid category.", "evidence": []}'
    )

    with pytest.raises(ValueError):
        classify_post("Test message")