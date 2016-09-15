import os
import smtplib


def send_mail(to, subject, body):
    server = 'smtp.gmail.com'
    port = 587

    gmail_address = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_PASSWORD"]

    headers = "\r\n".join(["From: " + gmail_address,
                           "Subject: " + subject,
                           "To: " + to,
                           "MIME-Version: 1.0",
                           "Content-Type: text/html"])

    session = smtplib.SMTP(server, port)
    session.ehlo()
    session.starttls()
    session.login(gmail_address, password)
    msg = (headers + "\r\n\r\n" + body).encode("utf-8")
    session.sendmail(gmail_address, to, msg)
    session.quit()
