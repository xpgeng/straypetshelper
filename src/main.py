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
    send_from_directory, flash, make_response, Response
import hashlib 
from time import strftime, localtime
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
#import flask.ext.login as UserMixin, login_required
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey
monkey.patch_all()

#####################constant variables#######################
#ROOT = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = ROOT+'/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.secret_key = 'super secret string'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #the max value of file size

###############login manager#################################
login_manager = LoginManager()
login_manager.init_app(app)





#class User(UserMixin):
    #pass
    #def __init__(self, name, id, active=True):
    #    self.name = name
    #    self.id = id
    #    self.active = active

    #def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        #return self.active

    #def is_anonymous(self):
    #    return False

    #def is_authenticated(self):
        #return True

##用户回调
#@login_manager.user_loader
#def load_user(userid):    
#    return User.get(userid)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_filename(filename):
    """
        This funcion can solve the bug of omitting the Chinese characters in filename.

    """
    if filename in ALLOWED_EXTENSIONS:
        filename_new = "%s.%s" % (int(time.time()), filename)
        return filename_new
    else:
        return filename


def save_image_return_url(filename, file):
    """ 
         return: the url of the image in the storage
    """
    c = Connection()
    bucket = c.get_bucket('imges')
    bucket.put_object(filename, file.read())
    return bucket.generate_url(filename)


def pets_number():
    """
        count the number of  the pets
    """
    kv = sae.kvdb.Client()
    if kv.get('petsnumber'):
        number = kv.get('petsnumber') + 1
        kv.replace('petsnumber', number)
        return number
    else:
        kv.set('petsnumber', 1)
        return 1
    kv.disconnect_all()

def users_number():
    """
        count the number of  the pets
    """
    kv = sae.kvdb.Client()
    if kv.get('usersnumber'):
        number = kv.get('usersnumber') + 1
        kv.replace('usersnumber', number)
        return number
    else:
        kv.set('usersnumber', 1)
        return 1
    kv.disconnect_all()


def save_data(pet_title,species,location,tel,supplement, photo_url):
    """
        key is like this form: 151204112340 which is convenient
        to search according to datetime.
    """
    item_number = pets_number()
    #print item_number
    print species
    kv = sae.kvdb.Client()
    if species == '狗狗':
        key = str('d'+strftime("%y%m%d%H%M%S" , localtime()))
    elif species == '猫猫':
        key = str('c'+strftime("%y%m%d%H%M%S" , localtime()))
    else:
        key = str('e'+strftime("%y%m%d%H%M%S" , localtime()))
    print key
    now = time.time()
    value = {'pet_title':pet_title, 'species': species,'location':location, 
        'tel':tel, 'supplement':supplement, 'photo_url':photo_url,'time':now}
    kv.set(key, value)
    kv.disconnect_all()

def save_user(username, password, email):
    """
    """
    usersnumber = users_number()
    kv = sae.kvdb.Client()
    user = str('u'+username)
    now = time.time()
    pwhash = generate_password_hash(password) #hash加密
    message = {'username':username, 'password':pwhash, 'email':email, 'time':now}
    kv.set(user, message)
    kv.disconnect_all()


def check_login(username,password):
    """
    """
    kv = sae.kvdb.Client()
    key = str('u'+username)
    pwhash = kv.get(key)['password']
    if check_password_hash(pwhash, password):
        return True
        print 12580
    else:
        return False

def check_user(username):
    kv = sae.kvdb.Client()
    key = str('u'+username)
    if kv.get(key):
        return True
    else:
        return False


@app.route('/')
def submit_pet():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def check_pet():
    pet_title = request.form['pet-title']
    species = request.form['species']
    location = request.form['location']
    tel = request.form['tel']
    supplement = request.form['supplement']
    pet_photo = request.files['petphoto']
    if pet_photo and allowed_file(pet_photo.filename):
        filename = secure_filename(pet_photo.filename)
        renew_filename = check_filename(filename)
        #pet_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], renew_filename))
        photo_url = save_image_return_url(renew_filename, pet_photo)
    save_data(pet_title,species,location,tel,supplement, photo_url)
    return render_template("check.html", pet_title=pet_title,
            species=species, location=location, tel=tel, supplement=supplement)


@app.route('/signup', methods=['GET','POST'])
def sign_up():
    message = None
    print request.method
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirmpassword = request.form['confirmpassword']
        print username, password, email, confirmpassword
        if check_user(username):
            message = '对不起, 您的用户名已经被注册.'
        elif password == confirmpassword:
            save_user(username, password, email)
            message = '注册成功!'
        else:
            message = '对不起,系统维护ing...'
    return render_template("signup.html", message = message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print username, password
        if not check_login(username,password):
            message = '用户名或密码不正确'
        else:
            #flash('登陆成功')
            #return redirect(url_for('submit_pet'))
            message = '登录成功!'
    return render_template('login.html', message = message)


@app.route('/show/<pet_species>', methods=['GET', 'POST'])
def show(pet_species):
    kv = sae.kvdb.Client()
    if pet_species == 'dog':
        prefix = 'd'
    elif pet_species == 'cat':
        prefix = 'c'
    else:
        prefix = 'e'
    images = [ value['photo_url']  for key,value in kv.get_by_prefix(prefix)]
    num = len(images)
    pet_pages = ['/petpage/'+ key for key, value in kv.get_by_prefix(prefix)]
    kv.disconnect_all()
    return render_template("show_pet.html",images=images,pet_species=pet_species,
        pet_pages = pet_pages,num = num)


@app.route('/petpage/<pet_id>')
def show_post(pet_id):
    # test:
    print pet_id
    kv = sae.kvdb.Client()
    pet_id = str(pet_id)
    pet_title = kv.get(pet_id)['pet_title']
    species = kv.get(pet_id)['species']
    tel = kv.get(pet_id)['tel']
    location = kv.get(pet_id)['location']
    supplement = kv.get(pet_id)['supplement']
    image = kv.get(pet_id)['photo_url']
    print pet_title, species, tel, location, supplement, image
    kv.disconnect_all()
    return render_template("petpage.html",pet_title=pet_title,
            species=species, location=location, tel=tel, supplement=supplement,
            image=image)


@app.route('/wechat_auth', methods=['GET', 'POST'])
def wechat_auth():  
    if request.method == 'GET':  
        token = 'xxxxxxxxxxx' # your token  
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