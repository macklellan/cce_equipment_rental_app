import smtplib
from email.mime.text import MIMEText
import os

smtp_host = os.environ['SMTP_SSL']
smtp_sender = os.environ['SMTP_SENDER']
smtp_pw = os.environ['SMTP_PW']

def new_res_notification(res_n, equipment, dates, name, email):

    # Email details
    sender = smtp_sender
    receiver = "ryan@carolinac-e.com, mackenzie@carolinac-e.com, aaron@carolinac-e.com"
    subject = "New Reservation: " + str(res_n)

    # body of email
    txt = "Please review the latest equipment reservation scheduled on the website."
    txt += "If reservation was created by an admin, please give access to renter/leasee."
    txt += "\n\n Name: " + name
    txt += "\n Email: " + email
    txt += "\n Dates: " + dates
    txt += "\n Equipment: " + equipment

    # Create message
    msg = MIMEText(txt)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    # Connect to SMTP server (e.g., Gmail)
    try:
        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_sender, smtp_pw)
            server.sendmail(smtp_sender, receiver, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


# new_res_notification(4, "2024_Bobcat_E26", "date1-date2", "Test Name", "testemail.com")
