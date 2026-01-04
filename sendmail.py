import smtplib
import ssl
from email.message import EmailMessage

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # For TLS
SENDER_EMAIL = "safecast.evm@gmail.com"
# Use the 16-character App Password, not your account password
SENDER_PASSWORD = "jquo hlqa zjgj rzxo" 

# Create the email message
msg = EmailMessage()
msg.set_content("Hello! This is a test email sent from Python.")
msg["Subject"] = "Test Email from Python"
msg["From"] = SENDER_EMAIL
msg["To"] = "psjoeljo@gmail.com"

# Send the email
context = ssl.create_default_context()

try:
    # Connect and upgrade to secure TLS
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context) 
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
