import logging
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def send_email_notification(email: str, username: str):
    # Read the text in template file
    with open("app/email_template.txt", "r") as file:
        email_content = file.read()

    final_message = email_content.replace("{username}", username)

    # Building the email package using with EmailMessage
    msg = EmailMessage()
    msg["Subject"] = "Welcome to the Real-Time Chat App!"
    msg["From"] = os.getenv("GMAIL_USER")
    msg["To"] = email  # <-- This will now accept ANY real email from Swagger while signing up
    msg.set_content(final_message)

    logger.info(f"[EMAIL SYSTEM] Attempting to send Gmail to: {email}")

    try:
        # Connecting to Gmail's server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Encryption to keep the password safe

            # Log into the server using .env credentials
            server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))

            # Passing the email to Google to deliver it
            server.send_message(msg)

        logger.info(f"[EMAIL SYSTEM] Real Gmail successfully delivered to {email}!")

    # In case of server failure
    except Exception as e:
        logger.error(f"[EMAIL SYSTEM] Gmail failed to send due to error: {e}")