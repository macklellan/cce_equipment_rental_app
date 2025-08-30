from mailersend import MailerSendClient, EmailBuilder
import os

admin_email_list = ['ryanmacklellan@gmail.com', 'ryanmcclellan2@gmail.com']

def new_res_notification(res_n, equipment, dates, name, email):

    ms = MailerSendClient(api_key=os.environ['MAILER_API'])

    txt = "Please review the latest equipment reservation scheduled on the website. <br>"
    txt += "If reservation was created by an admin, please give access to renter/leasee. <br>"
    txt += "<br> \n Name: " + name
    txt += "<br> \n Email: " + email
    txt += "<br> \n Dates: " + dates
    txt += "<br> \n Equipment: " + equipment

    emails = []

    for admin_email in admin_email_list:
        emails.append(EmailBuilder()
                 .from_email("admin@test-z0vklo6r8d1l7qrx.mlsender.net", "CCE RENTALS")
                 .to_many([{"email": admin_email, "name": "Admin"}])
                 .subject("CCE RENTALS: NEW RESERVATION #" + str(res_n))
                 .text(txt)
                 .html("<h3>" + txt + "</h3>")
                 .build())

    response = ms.emails.send_bulk(emails)
