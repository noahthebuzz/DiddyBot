from imap_tools import MailBox, MailboxLoginError, MailboxLogoutError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, json, re, time, traceback, imaplib, socket

def load_json_file(filename: str) -> dict:
    with open(filename) as f:
        print(f"Loading {filename}...")
        return json.load(f)

def load_email_credentials():
        return load_json_file('email_credentials.json')
    
def load_server_settings():
        return load_json_file('server_settings.json')
        
def load_recipients():
        recipients = load_json_file('recipients.json')
        new_recipients = []
        for recipient in recipients.values():
            new_recipients.append(recipient)
        return new_recipients

def fetch_emails(time: int, mailbox: MailBox, triggers: list) -> list:
        emails = []
        responses = mailbox.idle.wait(timeout=time*60)
        if responses:
                for email_msg in mailbox.fetch(mark_seen=False, criteria='UNSEEN'):
                        #print(f"[INFO]: New email found.")
                        for trigger in triggers:
                                if trigger.lower() in email_msg.from_.lower():
                                        emails.append(email_msg)
                                        break
                outgoing_emails = []
                for email_msg in emails:
                        body = email_msg.text
                        code_present = re.search(r"\D*(\d{6})\D*", body)
                        if code_present:
                                outgoing_emails.append(email_msg)
                print(f"[INFO]: Found {len(outgoing_emails)} emails with triggers.")
                return outgoing_emails
        else:
               print("[INFO]: No new emails found in the last 5min.")
               return None

def send_emails(emails: list, recipients: list, email_credentials: dict, server_settings: dict):
        try:
                # Connect to SMTP server
                server = smtplib.SMTP(server_settings['SMTP_SERVER'], server_settings['SMTP_PORT'])
                print(f"[SMTP_SERVER]: Connected to SMTP server.")
                server.starttls()
                server.login(email_credentials['EMAIL'], email_credentials['PASSWORD'])
                print(f"[SMTP_SERVER]: Logged in.")

                # Create email
                for email in emails:
                        forwarded_msg = MIMEMultipart()
                        forwarded_msg['From'] = email_credentials['EMAIL']
                        forwarded_msg['To'] = ", ".join(recipients)
                        forwarded_msg['Subject'] = f"FWD: {email.subject}"
                        forwarded_msg.attach(MIMEText(email.text, 'plain'))

                        # Send email
                        server.sendmail(email_credentials['EMAIL'], recipients, forwarded_msg.as_string())
                        print(f"[SMTP_SERVER]: Email [{email.subject}] forwarded to {recipients}.")
                server.quit()
                print(f"[SMTP_SERVER]: Disconnected from SMTP server.")
        except Exception as e:
                print(f"Error: {e}")
                        

def main():
        email_credentials = load_email_credentials()
        server_settings = load_server_settings()
        recipients = load_recipients()
        triggers = ["disney"]

        done = False
        while not done:
                try:
                        with MailBox(server_settings['IMAP_SERVER']).login(email_credentials['EMAIL'], email_credentials['PASSWORD'], 'INBOX') as mailbox:
                                try:
                                        print(f"[IMAP_SERVER]: Connected to IMAP server.")
                                        outgoing_emails = fetch_emails(1,mailbox, triggers)
                                        if outgoing_emails is not None:
                                                send_emails(outgoing_emails, recipients, email_credentials, server_settings)
                                        #mailbox.logout()
                                        #print(f"[IMAP_SERVER]: Disconnected from IMAP server.")
                                except KeyboardInterrupt:
                                        print("~KeyboardInterrupt")
                                        done = True
                                        break
                except (TimeoutError, ConnectionError, imaplib.IMAP4.abort, MailboxLoginError, MailboxLogoutError, socket.herror, socket.gaierror, socket.timeout) as e:
                        print(f'## Error\n{e}\n{traceback.format_exc()}\nreconnect in a 10sec...')
                        time.sleep(10)

if __name__ == "__main__":
        main()