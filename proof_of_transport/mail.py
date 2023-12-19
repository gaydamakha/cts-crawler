import smtplib

from email.message import EmailMessage


class MailClient:
    def __init__(self, from_email: str):
        self.from_email = from_email
        self.from_password = ''
        self.smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.smtp.login(self.from_email, self.from_password)

    def send_file_to(self, filepath: str, to_email: str) -> None:
        msg = EmailMessage()
        msg['Subject'] = 'Justificatif Transport'
        # me == the sender's email address
        # family = the list of all recipients' email addresses
        msg['From'] = self.from_email
        msg['To'] = to_email
        with open(filepath, 'rb') as fp:
            file_data = fp.read()
            msg.add_attachment(file_data, maintype='application',
                               subtype='pdf')
        self.smtp.send_message(msg)
