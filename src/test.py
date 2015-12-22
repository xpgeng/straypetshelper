# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, url_for, redirect
from flask import send_from_directory, flash, make_response, Response 
from flask.ext.mail import Mail, Message

app = Flask(__name__)
app.debug = True
app.secret_key = "a_random_secret_key_$%#!@"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mail=Mail(app)

app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.sina.com',
    MAIL_PORT=25,
    MAIL_USE_SSL=False,
    MAIL_USERNAME = 'namhyjeon@sina.com',
    MAIL_PASSWORD = 'cuiyuexing'
    )

mail=Mail(app)

@app.route('/')
def send_email():
    msg_title = 'mytest'
    recp_list=['huijuannan.p@gmail.com', 'namhyjeon@sina.com']
    recover_url="http://taketahome.sinaapp.com/reset/Imh1aWp1YW5uYW4ucEBnbWFpbC5jb20i.CVrfsw.lZLtwkJP6ohQngswgv5BkRTbJ9s"
    msg_body = render_template('email_reset.html', recover_url=recover_url)
    msg = Message(
              str(msg_title),
           sender='namhyjeon@sina.com',
           recipients=recp_list)
    msg.html = msg_body
    mail.send(msg)
    return "Sent"

if __name__ == "__main__":
    app.run(debug=True)