# -*- coding: utf-8 -*-
"""
Project: Stray Pets Helper
Author: Shenlang
        Huijuannan
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sae.kvdb
from flask import Flask, request, render_template, url_for, redirect
from flask import send_from_directory, flash, make_response, Response 
from flask.ext.login import LoginManager, UserMixin, login_required
from flask.ext.login import login_user, current_user, logout_user
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
import hashlib
from fun_user import save_email, users_number, check_email, check_login
from fun_user import add_to_emailset,get_message_petdict_from_userid,\
                 change_password
from pet import pets_number, save_data, change_sequence, del_pet 
from pet import get_petdict_according_petspecies, add_petkey_to_userId
from pet import get_image_and_petdict, search_results, check_message
from image import allowed_file, process_filename, save_image_return_url,\
                 get_photourls
from sae.ext.storage import monkey
from flask.ext.mail import Mail, Message
from wechat import wechat_interact 
monkey.patch_all()


################################
###### constant variables ######
################################
UNSIGNUP_USERNAME = set(['administrator', 'straypetshelper'])

app = Flask(__name__)
app.debug = True
app.secret_key = "a_random_secret_key_$%#!@"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)

mail=Mail(app)

app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.sina.com',
    MAIL_PORT=25,
    MAIL_USE_SSL=False,
    MAIL_USERNAME = 'straypetshelper@sina.com',
    MAIL_PASSWORD = 'dashener@py'
    )

mail=Mail(app)

login_serializer = URLSafeTimedSerializer(app.secret_key)
###########################
###### login manager ######
###########################
login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.init_app(app)


class User(UserMixin):
    
    def __init__(self, userid, password):
        self.id =userid 
        self.password = password
    
    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    @staticmethod
    def get(userid):
        kv = sae.kvdb.Client()
        emailset = kv.get('emailset')
        if emailset:
            for email in emailset:
                if email == userid:
                    password = kv.get(str(email))['password']
                    return User(email, password)
        else:
            return None
        kv.disconnect_all()


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@login_manager.token_loader
def load_token(token):
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
    data = login_serializer.loads(token, max_age=max_age)
    user = User.get(data[0])
    if user and data[1] == user.password:
        return user
    return None

def send_email(recp_list, msg_title, msg_body):
    msg = Message(
              str(msg_title),
           sender='straypetshelper@sina.com',
           recipients=recp_list)
    msg.html = msg_body
    mail.send(msg)
    return "Sent"


@app.route('/')
def show_all():
    return redirect(url_for('show', pet_species = 'all'))


@app.route('/submit')
@login_required
def submit_pet():
    user_id = current_user.get_id()
    return render_template('index.html', username=user_id)


@app.route('/submit', methods=['POST'])
def checkin_pet():
    user_id = current_user.get_id()  #user_id is email
    pet_title = request.form['pet-title']
    age = request.form['age']
    gender = request.form['gender']
    sterilization = request.form['sterilization'] 
    immunization = request.form['immunization'] 
    health = request.form['health']
    species = request.form['species']
    location = request.form['location']
    tel = request.form['tel']
    supplement = request.form['supplement']
    pet_photo = request.files.getlist('petphoto') # upload multiple files

    photo_urls = get_photourls(user_id, pet_photo)

    petkey = save_data(pet_title, age, gender, sterilization, immunization, \
        health, species,location,tel,supplement, photo_urls, user_id)

    add_petkey_to_userId( user_id, petkey)
    return redirect(url_for("show_post", pet_id=petkey, username=user_id))


@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    user_id = current_user.get_id()
    query = request.form['query']
    query = str(query)
    if not query:
        return render_template("nullpage.html")
    pet_dict = search_results(query)
    if pet_dict:
        return render_template('show_dict.html', pet_dict=pet_dict, username=user_id)
    else:
        return render_template("nullpage.html", username=user_id)


@app.route('/signup', methods=['GET','POST'])
def sign_up():
    message = None
    user_id = current_user.get_id()
    print request.method
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        if check_email(email):
            message = '对不起, 您的Email已经被注册.'
            return render_template("signup.html", message = message, username=user_id)
        elif len(password)<6 :
            message = '密码太短啦，再想一个长一点的吧:-）'
            return render_template("signup.html", message = message, username=user_id)
        elif password == confirmpassword:
            save_email(email, password, username)
            add_to_emailset(email)
            message = '注册成功!'
            user = User.get(str(email))
            login_user(user, remember=True)
            msg_title = "欢迎注册 带TA回家"
            msg_body = "亲爱的%s, 您好\n\n\t 欢迎您注册带TA回家。\n\t如果有任何的建议，请直接回复邮件。\n\n\t谢谢！"%username
            # send_email([str(email)], msg_title, msg_body)
            return redirect(url_for('show', pet_species = 'all')) 
        else:
            message = '确认密码和密码不一致，重新输入吧:-）'   
        return render_template("signup.html", message = message, username=user_id)
    else:
       return render_template("signup.html", message = message, username=user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    user_id = current_user.get_id()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get(str(email))
        if not check_login(email,password):
            message = '用户名或密码不正确'
            return render_template('login.html', message = message)
        else:
            login_user(user, remember=True)
            message = '登录成功!'
            return redirect(url_for('show', pet_species = 'all'))
    else:   
        return render_template('login.html', message = message, username=user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show', pet_species = 'all'))


@app.route('/show/<pet_species>', methods=['GET', 'POST'])
def show(pet_species):
    user_id = current_user.get_id()
    pet_dict = get_petdict_according_petspecies(pet_species)
    pet_dict = change_sequence(pet_dict)
    return render_template('show_dict.html', pet_dict=pet_dict, username=user_id)
       
############ test show page

# @app.route('/test', methods=['GET', 'POST'])
# def test():
#     user_id = current_user.get_id()
#     pet_dict = get_petdict_according_petspecies('all')
#     pet_dict = change_sequence(pet_dict)
#     return render_template('testShow.html', pet_dict=pet_dict, username=user_id)



@app.route('/petpage/<pet_id>')
def show_post(pet_id):
    user_id = current_user.get_id()
    image, pet_dict = get_image_and_petdict(pet_id) 
    return render_template("petpage.html", pet_id=pet_id, pet_dict=pet_dict, \
        num_photo=len(image), image=image, username=user_id)


@app.route('/delete_pet', methods=['GET', 'POST'])
def delete_pet():
    user_id = current_user.get_id()
    pet_id = request.form['pet_id']
    pet_id = str(pet_id)
    user_id = str(user_id)
    del_pet(pet_id, user_id)
    return redirect(url_for('usercenter'))


@app.route('/usercenter')
@login_required
def usercenter():
    user_id = current_user.get_id()
    message, pet_dict = get_message_petdict_from_userid(user_id)
    pet_dict = change_sequence(pet_dict)
    return render_template('user_page.html', message=message, 
        pet_dict=pet_dict, username=user_id)


@app.route('/reset', methods=['GET','POST'])
def reset():
    user_id = current_user.get_id()
    if request.method == 'POST':
        email = request.form['email']
        if check_email(email):
            msg_title = "找回「带TA回家」的账户密码"

            token = login_serializer.dumps(email, salt='recover-key')
            recover_url = url_for('reset_with_token', token=token, _external=True)

            msg_body = render_template('email_reset.html', recover_url=recover_url)
            send_email([str(email)], msg_title, msg_body)
            message = """已经向你的邮箱 %s发送了一封邮件，请根据其中的指示操作。
                （提示：邮件可能会被识别为垃圾邮件）""" % email
        else:
            message = "此邮箱没有注册，请重新输入或者注册"
        return render_template('reset.html',message=message, username=user_id)

    return render_template('reset.html', username=user_id)



@app.route('/reset/<token>',methods=['GET','POST'])
def reset_with_token(token):
    user_id = current_user.get_id()
    try:
        email = login_serializer.loads(token, salt = "recover-key", max_age = 86400)
    except:
        abort(404)

    if request.method == 'POST':
        password = request.form['password']
        change_password(email, password)
        message = "密码修改成功，请重新登录"
        return render_template('login.html', message = message, username=user_id)
    return render_template('reset_with_token.html', email=email, token=token, username=user_id)




@app.route('/about_us')
def about_us():
    user_id = current_user.get_id()
    return render_template("us_about.html", username=user_id)



@app.route('/client', methods=['GET','POST'])
def client():
    message = request.form['data']
    print message
    print check_message(message)
    return check_message(message)


@app.route('/wechat', methods=['GET', 'POST'])
def wechat_auth():  
    if request.method == 'GET':  
        token = 'straypets' # your token  
        query = request.args  # GET 方法附上的参数  
        signature = query.get('signature', '')  
        timestamp = query.get('timestamp', '')  
        nonce = query.get('nonce', '')  
        echostr = query.get('echostr', '')  
        s = [timestamp, nonce, token]  
        s.sort()  
        s = ''.join(s)  
        if ( hashlib.sha1(s).hexdigest() == signature ):   
            return make_response(echostr)
    else:
        msg_dict = request.stream.read()
        return wechat_interact(msg_dict)

        



if __name__ == "__main__":
    app.run(debug=True)