# Luxia Companion

Agente WhatsApp que responde parceiros comerciais sobre cotas de usinas de energia solar. Powered by CrewAI + RAG (ChromaDB) + Twilio + FastAPI.

## Arquitetura

```
WhatsApp → Twilio Webhook → FastAPI → CrewAI Agent → ChromaDB RAG → Twilio Reply → WhatsApp
```

## Setup Local

### 1. Instalar dependências

```bash
pip install -e ".[dev]"
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Ingerir documentos

Coloque PDFs e arquivos Markdown em `knowledge_base/`, depois:

```bash
python scripts/ingest.py        # Ingerir documentos
python scripts/ingest.py --clear  # Limpar e re-ingerir
```

### 4. Rodar o servidor

```bash
uvicorn luxia_companion.main:app --reload --port 8000
```

### 5. Expor via ngrok (para testes com Twilio)

```bash
ngrok http 8000
```

Configure o webhook no Twilio Console:
- URL: `https://<seu-ngrok>.ngrok-free.app/webhook/whatsapp`
- Method: POST

## Docker

```bash
# Produção
docker compose up -d

# Desenvolvimento (com ngrok)
docker compose --profile dev up -d
```

Dashboard ngrok: http://localhost:4040

## Testes

```bash
pytest
```

## Estrutura

```
src/luxia_companion/
├── main.py           # FastAPI app + webhook
├── config.py         # Settings (env vars)
├── crew.py           # CrewAI agent orchestration
├── config/
│   ├── agents.yaml   # Agent definitions
│   └── tasks.yaml    # Task definitions
├── tools/
│   └── knowledge_search.py  # RAG search tool
├── knowledge/
│   ├── store.py      # ChromaDB wrapper
│   └── ingestion.py  # Document parsing + chunking
└── whatsapp/
    └── client.py     # Twilio send/validate helpers
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_WHATSAPP_FROM` | Número WhatsApp Twilio (ex: `whatsapp:+14155238886`) |
| `OPENAI_API_KEY` | Chave API OpenAI |
| `OPENAI_MODEL_NAME` | Modelo LLM (default: `gpt-4o`) |
| `CHROMA_PERSIST_DIR` | Diretório ChromaDB (default: `./chroma_data`) |
| `KNOWLEDGE_BASE_DIR` | Diretório dos documentos (default: `./knowledge_base`) |
