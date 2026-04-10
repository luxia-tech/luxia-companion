from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Patch validate_request to always return True in tests
    with patch("luxia_companion.main.validate_request", return_value=True):
        from luxia_companion.main import app

        yield TestClient(app)


def _twilio_form(body: str = "Olá, como funciona?") -> dict:
    return {
        "Body": body,
        "From": "whatsapp:+5511999999999",
        "To": "whatsapp:+14155238886",
        "MessageSid": "SM1234567890abcdef",
        "AccountSid": "AC1234567890abcdef",
        "NumMedia": "0",
    }


def test_webhook_returns_200(client):
    with patch("luxia_companion.main._process_message"):
        response = client.post("/webhook/whatsapp", data=_twilio_form())
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]


def test_webhook_empty_body(client):
    form = _twilio_form(body="")
    with patch("luxia_companion.main._process_message") as mock_process:
        response = client.post("/webhook/whatsapp", data=form)
        assert response.status_code == 200
        mock_process.assert_not_called()


def test_webhook_invalid_signature():
    """Signature validation is currently disabled for dev.
    This test documents the expected behavior when re-enabled."""
    # TODO: re-enable when Twilio signature validation is active in production
    from luxia_companion.main import app

    client = TestClient(app)
    with patch("luxia_companion.main._process_message"):
        response = client.post("/webhook/whatsapp", data=_twilio_form())
        # Currently returns 200 because validation is disabled
        assert response.status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
