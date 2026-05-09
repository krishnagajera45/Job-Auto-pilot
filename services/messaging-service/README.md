# Messaging Service

## Responsibilities
- Accepts inbound messages from Telegram and WhatsApp webhooks.
- Normalizes job links or job descriptions.
- Triggers OpenClaw agent workflows and document rendering.
- Sends PDFs/DOCX files back via notifications service.

## Key Endpoints
- `POST /v1/channels/intake`
