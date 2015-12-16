# -*- coding: utf-8 -*-
"""
Project: Stray Pets Helper
Author: Shenlang
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import sae.kvdb
import time
from flask import Flask, request, render_template, url_for, \
       send_from_directory, flash, make_response, Response, redirect
import hashlib 
from time import strftime, localtime
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, \
        check_password_hash
from flask.ext.login import LoginManager, UserMixin, login_required, \
 login_user, current_user, logout_user
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
from fun_user import save_email, users_number, check_email, check_login, add_to_emailset
from pet import pets_number, save_data, change_sequence, del_pet

monkey.patch_all()

#####################constant variables#######################
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UNSIGNUP_USERNAME = set(['administrator', 'straypetshelper'])

app = Flask(__name__)
app.debug = True
app.secret_key = "a_random_secret_key_$%#!@"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)

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
            kv = sae.kvdb.Client()
        else:
            return None


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def process_filename(user_id,filename):
    """
          preprocess filename
    """
    filename_new = "%s%s.%s" % (user_id, int(time.time()), filename)
    return filename_new

def save_image_return_url(filename, file):
    """ 
         return: the url of the image in the storage
    """
    c = Connection()
    bucket = c.get_bucket('images')
    bucket.put_object(filename, file.read())
    return bucket.generate_url(filename)



@app.route('/')
def show_all():
    #user_id = (current_user.get_id()) or None)
    return redirect(url_for('show', pet_species = 'all'))#user_id=user_id

@app.route('/submit')
@login_required
def submit_pet():
    user_id = current_user.get_id()
    return render_template('index.html', username=user_id)

@app.route('/submit', methods=['POST'])
def checkin_pet():
    user_id = current_user.get_id()  #user_id is email
    pet_title = request.form['pet-title']
    species = request.form['species']
    location = request.form['location']
    tel = request.form['tel']
    supplement = request.form['supplement']
    pet_photo = request.files['petphoto']
    if pet_photo and allowed_file(pet_photo.filename):
        filename = secure_filename(pet_photo.filename)
        renew_filename = process_filename(user_id, filename)
        photo_url = save_image_return_url(renew_filename, pet_photo)
    petkey = save_data(pet_title,species,location,tel,supplement, photo_url, user_id)

    kv = sae.kvdb.Client()
    user_dic = kv.get(str(user_id))
    user_dic['pet'].append(str(petkey))
    kv.set(str(user_id),user_dic)
    kv.disconnect_all()
    return redirect(url_for("show_post", pet_id=petkey, username=user_id))


@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    query = request.form['query']
    query = str(query)
    if not query:
        return render_template("nullpage.html")
    kv = sae.kvdb.Client()
    data = kv.get_by_prefix('s')
    results = []
    for key, value in data:
        pet_item = [value['pet_title'], value['species'], value['location'],\
            value['supplement'], value['date'], value['email']]
        for item in pet_item:
            if query in str(item):
                results.append(key)
    if results:
        print type(kv.get_multi(results).items())
        pet_dict = kv.get_multi(results).items()
        pet_dict = change_sequence(pet_dict)
        return render_template('show_dict.html', pet_dict=pet_dict)
    else:
        return render_template("nullpage.html")


@app.route('/signup', methods=['GET','POST'])
def sign_up():
    message = None
    print request.method
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        if check_email(email):
            message = '对不起, 您的Email已经被注册.'
            return render_template("signup.html", message = message)
        elif password == confirmpassword:
            save_email(email, password, username)
            add_to_emailset(email)
            message = '注册成功!'
            user = User.get(str(email))
            login_user(user, remember=True)
            return redirect(url_for('show', pet_species = 'all')) 
        else:
            message = '对不起,系统维护ing...'   
        return render_template("signup.html", message = message)
    else:
       return render_template("signup.html", message = message) 


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get(str(email))
        print email, password
        if not check_login(email,password):
            message = '用户名或密码不正确'
            return render_template('login.html', message = message)
        else:
            login_user(user, remember=True)
            message = '登录成功!'
            return redirect(url_for('show', pet_species = 'all'))
    else:   
        return render_template('login.html', message = message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show', pet_species = 'all'))

@app.route('/show/<pet_species>', methods=['GET', 'POST'])
def show(pet_species):
    user_id = current_user.get_id()
    kv = sae.kvdb.Client()
    if pet_species == 'dog':
        prefix = 's:d'
    elif pet_species == 'cat':
        prefix = 's:c'
    elif pet_species == 'all':
        prefix = 's:'
    else:
        prefix = 's:e'
    keys = [key for key, value in kv.get_by_prefix(prefix)]
    pet_dict = kv.get_multi(keys).items()
    pet_dict = change_sequence(pet_dict)
    return render_template('show_dict.html', pet_dict=pet_dict, username=user_id)
    
    

@app.route('/petpage/<pet_id>')
def show_post(pet_id):
    user_id = current_user.get_id()
    kv = sae.kvdb.Client()
    pet_id = str(pet_id)
    pet_title = kv.get(pet_id)['pet_title']
    species = kv.get(pet_id)['species']
    tel = kv.get(pet_id)['tel']
    location = kv.get(pet_id)['location']
    supplement = kv.get(pet_id)['supplement']
    image = kv.get(pet_id)['photo_url']
    kv.disconnect_all()
    return render_template("petpage.html",pet_title=pet_title,
            species=species, location=location, tel=tel, supplement=supplement,
            image=image, pet_id=pet_id, username=user_id)

@app.route('/delete_pet', methods=['GET', 'POST'])
def delete_pet():
    pet_id = request.form['pet_id']
    pet_id = str(pet_id)
    del_pet(pet_id)
    return redirect(url_for('show', pet_species = 'all'))


@app.route('/usercenter')
@login_required
def usercenter():
    user_id = current_user.get_id()
    kv = sae.kvdb.Client()
    keys = kv.get(str(user_id))['pet']
    if not keys:
        message = "你还没有发布过小动物信息哦，快去发布吧～"
    else:
        message = "您发布过的小动物："       
    pet_dict = kv.get_multi(keys).items()
    pet_dict = change_sequence(pet_dict)
    return render_template('user_page.html', message=message, 
        pet_dict=pet_dict, username=user_id)



@app.route('/about_us')
def about_us():
    user_id = current_user.get_id()
    return render_template("us_about.html", username=user_id)



@app.route('/wechat_auth', methods=['GET', 'POST'])
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

#@app.route('/wechat', methods['GET', 'POST'])
#def 
# Here is used for wechat interaction


if __name__ == "__main__":
    app.run(debug=True)