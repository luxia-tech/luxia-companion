import logging

from twilio.rest import Client
from twilio.request_validator import RequestValidator

from luxia_companion.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None

WHATSAPP_MAX_LENGTH = 1600


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def send_message(to: str, body: str) -> str:
    if len(body) > WHATSAPP_MAX_LENGTH:
        body = body[: WHATSAPP_MAX_LENGTH - 3] + "..."

    client = _get_client()
    message = client.messages.create(
        from_=settings.twilio_whatsapp_from,
        to=to,
        body=body,
    )
    logger.info(f"Mensagem enviada para {to}: {message.sid}")
    return message.sid


def validate_request(url: str, params: dict, signature: str) -> bool:
    validator = RequestValidator(settings.twilio_auth_token)
    return validator.validate(url, params, signature)
