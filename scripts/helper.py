import smtplib
from email.mime.text import MIMEText


def notify(msg, to, password):
    msg = MIMEText(msg)
    msg['To'] = to
    msg['Subject'] = 'Notification'

    s = smtplib.SMTP()
    s.connect('smtp.strato.de', 587)
    s.login('willi@raschkowski.com', password)
    s.sendmail('willi@raschkowski.com', ['willi@raschkowski.com'], msg.as_string())
    s.quit()
