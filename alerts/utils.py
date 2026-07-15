from twilio.rest import Client
from django.conf import settings

def send_alert_sms(message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=settings.TECHNICIAN_PHONE
        )
        print("✅ SMS sent:", message)
    except Exception as e:
        print("❌ Error sending SMS:", e)
