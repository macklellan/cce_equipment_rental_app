from mailersend import MailerSendClient, EmailBuilder
import os


def res_update_notification():
        ms = MailerSendClient(api_key=os.environ['MAILER_API'])


        email = (EmailBuilder()
                 .from_email("admin@test-z0vklo6r8d1l7qrx.mlsender.net", "CCE RENTALS")
                 .to_many([{"email": "ryanmcclellan2@gmail.com", "name": "Ryan McClellan"}])
                 .subject("Hello from MailerSend!")
                 .html("<h1>Hello World!</h1>")
                 .text("Hello World!")
                 .build())

        response = ms.emails.send(email)


res_update_notification()