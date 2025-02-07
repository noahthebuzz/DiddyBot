import json
import subprocess
import getpass

# Dateinamen für die JSON-Dateien
CREDENTIALS_FILE = "email_credentials.json"
RECIPIENTS_FILE = "recipients.json"
SERVER_SETTINGS_FILE = "server_settings.json"

# Filenames for configs
REQUIREMENTS_FILE = "requirements.txt"


def install_dependencies():
    """ Installs all required Python packages """
    print("📦 Installing dependencies...")
    subprocess.run(["pip", "install", "-r", REQUIREMENTS_FILE], check=True)
    print("✅ Dependencies installed!")


def get_input(prompt):
    """ Gets user input. """
    user_input = input(f"{prompt}: ")
    return user_input


def write_json(filename, data):
    """ Writes data to a file. """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Saved in {filename}!")


def setup_email_credentials():
    """ Requests email login data and saves it in email_credentials.json. """
    print("\n\n🔑 Put in your E-Mail Login Information:\n--------------------------------------")
    email = get_input("E-Mail Address\n  > ")
    password = getpass.getpass("Password (will be stored unencrypted locally on your device!)\n  > ")

    data = {"EMAIL": email, "PASSWORD": password}
    write_json(CREDENTIALS_FILE, data)

    print(f"✅ Saved in {CREDENTIALS_FILE}!")


def setup_recipients():
    """ Queries the recipient emails and saves them in recipients.json. """
    print("\n\n📨 Put in the recipients' e-mails for forwarded e-mails:\n--------------------------------------")
    recipients = {}
    count = 1

    while True:
        email = get_input(f"Recipient {count} (leave blank to finish)\n  > ")
        if not email:
            break
        recipients[str(count)] = email
        count += 1

    write_json(RECIPIENTS_FILE, recipients)

    print(f"✅ Saved in {RECIPIENTS_FILE}!")


def setup_server_settings():
    """ Saves the default values for IMAP & SMTP in server_settings.json. """
    print("\n\n⚙️  Put in the e-mail server settings:\n--------------------------------------")
    imap_server = get_input("IMAP-Server\n  > ")
    imap_port = int(get_input("IMAP-Port\n  > "))
    smtp_server = get_input("SMTP-Server\n  > ")
    smtp_port = int(get_input("SMTP-Port\n  > "))

    data = {
        "IMAP_SERVER": imap_server,
        "IMAP_PORT": imap_port,
        "SMTP_SERVER": smtp_server,
        "SMTP_PORT": smtp_port,
    }

    write_json(SERVER_SETTINGS_FILE, data)
    print(f"✅ Saved in {SERVER_SETTINGS_FILE}!")


def main():
    print("🚀 Setup for the e-mail forwarding script\n")

    # Abhängigkeiten installieren
    install_dependencies()

    # JSON-Konfigurationsdateien erstellen
    setup_email_credentials()
    setup_server_settings()
    setup_recipients()

    print("\n\n🎉 Setup completed! You can now start the script with:")
    print("   python main.py")


if __name__ == "__main__":
    main()