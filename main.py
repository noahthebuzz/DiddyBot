import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
import re

# Email credentials
def load_email_credentials() -> dict:
    with open('email_credentials.json') as f:
        credentials = json.load(f)
    with open('server_settings.json') as f:
        credentials.update(json.load(f))
    return credentials

# Recipients emails
def load_recipients() -> dict:
    with open('recipients.json') as f:
        return json.load(f)

def check_mails_for(TRIGGERWORD: str, IMAP_SERVER: str, EMAIL_ACCOUNT: str, EMAIL_PASSWORD: str, SMTP_SERVER: str, SMTP_PORT: int, FORWARD_TO: dict):
    try:
        # Connect to IONOS IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        # Suche nach UNGELESENEN Nachrichten
        result, data = mail.search(None, "UNSEEN")
        mail_ids = data[0].split()

        for num in mail_ids:
            result, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Absender zuerst prüfen (schneller als den Body zu analysieren)
            sender = msg["From"]
            if TRIGGERWORD.lower() not in sender.lower():
                continue  # Falls Absender nicht passt, nächste E-Mail prüfen

            # Falls Sender passt, jetzt den Body analysieren
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            # Regex für den 6-stelligen Code zwischen ">" und "<"
            match = re.search(r">\D*(\d{6})\D*<", body)
            if match:
                #confirmation_code = match.group(1)  # Nur den Code speichern
                #print(f"✅ Bestätigungscode {confirmation_code} gefunden in E-Mail von {sender}.")
                
                # E-Mail weiterleiten
                for recipient in FORWARD_TO.values():
                    forward_email(msg, SMTP_SERVER, SMTP_PORT, EMAIL_ACCOUNT, EMAIL_PASSWORD, recipient)
            #else:
                #print(f"❌ Kein gültiger Code in E-Mail von {sender}")

        mail.logout()

    except Exception as e:
        print("[ERROR]:\n", e)

    
def forward_email(original_msg, SMTP_SERVER, SMTP_PORT, EMAIL_ACCOUNT, EMAIL_PASSWORD, RECIPIENT):
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

        # Create new email
        forwarded_msg = MIMEMultipart()
        forwarded_msg["From"] = EMAIL_ACCOUNT
        forwarded_msg["To"] = RECIPIENT
        forwarded_msg["Subject"] = f"FWD: {original_msg['Subject']}"
        
        # Get email content
        body = ""
        if original_msg.is_multipart():
            for part in original_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
        else:
            body = original_msg.get_payload(decode=True).decode()
        
        forwarded_msg.attach(MIMEText(body, "plain"))

        # Send the email
        server.sendmail(EMAIL_ACCOUNT, RECIPIENT, forwarded_msg.as_string())
        server.quit()
        print(f"✅ E-Mail weitergeleitet: {original_msg['Subject']}")

    except Exception as e:
        print("❌ Forwarding Error:", e)


if __name__ == '__main__':
    credentials = load_email_credentials()
    recipients = load_recipients()

    TRIGGERWORD = "disney"  # Hier den Absendernamen anpassen

    while True:
        check_mails_for(
            TRIGGERWORD,
            credentials["imapserver"],
            credentials["email"],
            credentials["password"],
            credentials["smtpserver"],
            credentials["smtpport"],
            recipients
        )
        print("⏳ Warte 20 Sekunden auf die nächste Überprüfung...")
        time.sleep(20)