import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from luxia_companion.config import settings
from luxia_companion.crew import answer
from luxia_companion.knowledge.store import count
from luxia_companion.knowledge.ingestion import ingest_all
from luxia_companion.whatsapp.client import send_message, validate_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-ingest knowledge base if empty (e.g. fresh container)
    try:
        if count() == 0:
            logger.info("Base de conhecimento vazia — iniciando ingestão automática...")
            result = ingest_all()
            logger.info(f"Ingestão concluída: {result['files']} arquivos, {result['chunks']} chunks")
        else:
            logger.info(f"Base de conhecimento já populada ({count()} chunks)")
    except Exception:
        logger.exception("Erro na ingestão automática — a app continuará sem base")
    yield


app = FastAPI(title="Luxia Companion", version="0.1.0", lifespan=lifespan)


def _process_message(from_number: str, body: str, message_sid: str) -> None:
    logger.info(f"Processando mensagem {message_sid} de {from_number}: {body[:80]}")
    try:
        response_text = answer(body)
        send_message(to=from_number, body=response_text)
        logger.info(f"Resposta enviada para {from_number} (msg {message_sid})")
    except Exception:
        logger.exception(f"Erro ao processar mensagem {message_sid}")
        try:
            send_message(
                to=from_number,
                body="Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes.",
            )
        except Exception:
            logger.exception("Falha ao enviar mensagem de erro")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()

    # Validate Twilio signature (disabled during dev/tunnel testing)
    # TODO: re-enable in production
    # signature = request.headers.get("X-Twilio-Signature", "")
    # url = str(request.url)
    # params = {k: v for k, v in form_data.items()}
    # if not validate_request(url, params, signature):
    #     logger.warning(f"Assinatura Twilio inválida de {form_data.get('From', '?')}")
    #     raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    body = str(form_data.get("Body", "")).strip()
    from_number = str(form_data.get("From", ""))
    message_sid = str(form_data.get("MessageSid", ""))

    if not body:
        logger.info(f"Mensagem vazia de {from_number}, ignorando")
        return Response(
            content=str(MessagingResponse()), media_type="application/xml"
        )

    logger.info(f"Recebido de {from_number}: {body[:80]}")

    background_tasks.add_task(_process_message, from_number, body, message_sid)

    # Respond immediately to Twilio (empty TwiML = no auto-reply)
    return Response(content=str(MessagingResponse()), media_type="application/xml")


@app.get("/health")
async def health():
    return {"status": "ok"}
