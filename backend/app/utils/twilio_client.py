from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM


def send_whatsapp_message(to_phone: str, message: str) -> None:
    """Send a WhatsApp message via Twilio. Raises on failure."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise ValueError("Twilio credentials not configured")
    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    to_number = f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_FROM,
        to=to_number,
    )
