from threading import Thread
from app import mail
from flask_mail import Message
from flask import current_app, render_template
from app.libs.error_code import EmailSendError


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            raise EmailSendError()


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message('bupt' + ' ' + subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to]
                  )
    msg.html = render_template(template, **kwargs)
    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
