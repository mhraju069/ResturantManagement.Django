import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        """
        Sends email messages via Brevo's v3 transactional email API.
        """
        if not email_messages:
            return 0
        
        api_key = getattr(settings, 'BREVO_API_KEY', None)
        sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', None))
        sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Varivo')

        if not api_key:
            if self.fail_silently:
                return 0
            raise ValueError("BREVO_API_KEY is not defined in Django settings.")

        if not sender_email:
            if self.fail_silently:
                return 0
            raise ValueError("Sender email is not configured (set DEFAULT_FROM_EMAIL or BREVO_SENDER_EMAIL).")

        count = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        for message in email_messages:
            # Extract HTML content from alternatives if available
            html_content = None
            if hasattr(message, 'alternatives') and message.alternatives:
                for alt_content, alt_mimetype in message.alternatives:
                    if alt_mimetype == 'text/html':
                        html_content = alt_content
                        break
            
            # Fallback to checking the message content subtype
            if not html_content and getattr(message, 'content_subtype', None) == 'html':
                html_content = message.body

            # Build the recipients list
            to_list = [{"email": email} for email in message.to]
            
            # Prepare payload according to Brevo API specification
            payload = {
                "sender": {
                    "name": sender_name,
                    "email": sender_email
                },
                "to": to_list,
                "subject": message.subject,
            }
            
            if html_content:
                payload["htmlContent"] = html_content
            
            if message.body:
                payload["textContent"] = message.body

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                if response.status_code in [200, 201]:
                    count += 1
                    logger.info(f"Email successfully sent to {message.to} via Brevo. Message ID: {response.json().get('messageId')}")
                else:
                    logger.error(f"Failed to send email to {message.to} via Brevo. Status: {response.status_code}. Response: {response.text}")
                    if not self.fail_silently:
                        raise Exception(f"Brevo API error: {response.status_code} - {response.text}")
            except Exception as e:
                logger.exception(f"Exception raised while sending email to {message.to} via Brevo")
                if not self.fail_silently:
                    raise e
                    
        return count
