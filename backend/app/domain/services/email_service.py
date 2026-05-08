import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # In a real app, you would configure SendGrid, Mailgun, or AWS SES here
        self.provider = "Mock Email Provider"

    def send_alert(self, user_email: str, subject: str, message: str) -> bool:
        """
        Sends an email alert to the user.
        For MVP, this simply logs to the console to simulate email delivery without external API costs.
        """
        try:
            # Simulated Email Delivery
            border = "=" * 50
            email_output = f"""
{border}
[MOCK EMAIL DELIVERED via {self.provider}]
To: {user_email}
Subject: {subject}
{border}
{message}
{border}
            """
            print(email_output)
            logger.info(f"Email successfully 'sent' to {user_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

email_service = EmailService()
