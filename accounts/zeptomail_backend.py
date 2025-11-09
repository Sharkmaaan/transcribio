import os
import json
import requests
from django.core.mail.backends.base import BaseEmailBackend

class ZeptoMailAPIBackend(BaseEmailBackend):
    """
    Django EmailBackend for ZeptoMail HTTP REST API
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        api_url = "https://api.zeptomail.eu/v1.1/email"
        api_token = os.environ.get("ZEPTOMAIL_API_TOKEN")  # Env variable for token

        if not api_token:
            if not self.fail_silently:
                print("ERROR: ZEPTOMAIL_API_TOKEN not set in environment.")
            return 0

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Zoho-enczapikey {api_token}"
        }

        for message in email_messages:
            to_list = []
            for addr in message.to:
                to_list.append({"email_address": {"address": addr}})

            payload = {
                "from": {"address": message.from_email},
                "to": to_list,
                "subject": message.subject,
                "htmlbody": message.body,  # Supports HTML
            }

            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
                response.raise_for_status()
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    print(f"Error sending email via ZeptoMail API: {e}")

        return sent_count
