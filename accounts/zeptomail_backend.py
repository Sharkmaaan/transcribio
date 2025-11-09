import os
import json
import requests
from email.utils import parseaddr
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

            # Ensure `from` contains a bare email address and optional name
            raw_from = message.from_email or os.environ.get("MAIL_FROM_ADDRESS", "")
            name, email_addr = parseaddr(str(raw_from))
            # fallback to MAIL_FROM_ADDRESS env if parsing failed
            if not email_addr:
                fallback = os.environ.get("MAIL_FROM_ADDRESS", "")
                name2, email_addr2 = parseaddr(fallback)
                name = name or name2
                email_addr = email_addr or email_addr2

            from_field = {"address": email_addr}
            if name:
                from_field["name"] = name

            # Build payload without the `agent` key (ZeptoMail reported agent as extra key)
            payload = {
                "from": from_field,
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
