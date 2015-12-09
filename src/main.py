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
from flask import Flask, request, render_template, url_for, send_from_directory, flash
from time import strftime, localtime
from werkzeug import secure_filename
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey
monkey.patch_all()

#####################constant variables#######################
#ROOT = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = ROOT+'/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



app = Flask(__name__)
app.secret_key = 'some_secret'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #the max value of file size



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
    print item_number
    kv = sae.kvdb.Client()
    key = strftime("%y%m%d%H%M%S" , localtime())
    print key
    now = time.time()
    value = {'pet_title':pet_title, 'species': species,'location':location, 
        'tel':tel, 'supplement':supplement, 'photo_url':photo_url,'time':now}
    kv.set(key, value)
    kv.disconnect_all()

def save_user(username, password, email):
    usersnumber = users_number()
    kv = sae.kvdb.Client()
    user = str('u'+username) #防止用户输入数字与pet data的key 相撞, 同时能根据'u'快速搜索username
    now = time.time()
    message = {'username':username, 'password':password, 'email':email, 'time':now}
    kv.set(user, message)
    kv.disconnect_all()


def check_login(username,password):
    """
    """
    kv = sae.kvdb.Client()
    key = str('u'+username)
    print key
    if password == kv.get(key)['password']:
        return True
        print 12580
    else:
        return False



@app.route('/')
def submit_pet():
    return render_template("index.html")

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
        if password == confirmpassword:
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
    

#@app.route('/edit', methods=["POST"])
#def edit():
#    content = request.form["editContent"]
##    tags = tags_process(request.form["editTags"])
#    data_store(content, tags)
#    flash("数据提交成功")
#    return redirect( url_for('index') )


#@app.route('/', methods=['POST'])


if  __name__ == "__main__":
    app.run(debug=True)