# alerts/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_alert_email(message):
    """
    Send an alert email to the technician using Zoho SMTP.
    """
    subject = "⚠️ Oxygen Monitoring Alert"
    recipient = getattr(settings, "TECHNICIAN_EMAIL", None)

    if recipient:
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # must be set in settings.py
                [recipient],
                fail_silently=False,
            )
            print("✅ Email sent:", message)
        except Exception as e:
            print("❌ Error sending email:", e)

