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
        api_token = (os.environ.get("ZEPTOMAIL_API_TOKEN") or "").strip()  # Env variable for token

        if not api_token:
            if not self.fail_silently:
                print("ERROR: ZEPTOMAIL_API_TOKEN not set in environment.")
            return 0

        # Build Authorization header.
        # Accept either a full header value stored in the env (e.g. "Zoho-enczapikey ...")
        # or just the raw token. This avoids misconfiguration that causes 401.
        if api_token.lower().startswith("zoho-enczapikey"):
            auth_value = api_token
        elif api_token.startswith("Zoho-enczapikey"):
            auth_value = api_token
        else:
            auth_value = f"Zoho-enczapikey {api_token}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth_value,
        }

        for message in email_messages:
            to_list = []
            for addr in message.to:
                to_list.append({"email_address": {"address": addr}})

            # Ensure from-address is a real email; fall back to MAIL_FROM_ADDRESS env var
            from_address = message.from_email
            if not from_address or "@" not in str(from_address):
                from_address = os.environ.get("MAIL_FROM_ADDRESS", from_address)

            payload = {
                "from": {"address": from_address},
                # include agent id only if provided in env
                **({"agent": os.environ.get("ZEPTOMAIL_AGENT_ID")} if os.environ.get("ZEPTOMAIL_AGENT_ID") else {}),
                "to": to_list,
                "subject": message.subject,
                "htmlbody": message.body,  # Supports HTML
            }

            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
                # Log full response for debugging and count only 2xx as sent
                if 200 <= response.status_code < 300:
                    sent_count += 1
                else:
                    if not self.fail_silently:
                        print("ZeptoMail API request failed",
                              "status=", response.status_code,
                              "body=", response.text,
                              "payload=", json.dumps(payload))
            except Exception as e:
                if not self.fail_silently:
                    # Try to include response details if available
                    resp = getattr(e, 'response', None)
                    if resp is not None:
                        print(f"ZeptoMail request exception: {e}, status={resp.status_code}, body={resp.text}")
                    else:
                        print("Error sending email via ZeptoMail API:", e)

        return sent_count
