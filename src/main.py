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


def count_items():
    """
        count the number of  the items or pets
    """
    kv = sae.kvdb.Client()
    if kv.get('NumberOfItems'):
        number = kv.get('NumberOfItems') + 1
        kv.replace('NumberOfItems', number)
        return number
    else:
        kv.set('NumberOfItems', 1)
        return 1
    kv.disconnect_all()


def save_data(pet_title,species,location,tel,supplement, photo_url):
    """
        key is like this form: 151204112340 which is convenient
        to search according to datetime.
    """
    item_number = count_items()
    print item_number
    kv = sae.kvdb.Client()
    key = strftime("%y%m%d%H%M%S" , localtime())
    print key
    now = time.time()
    value = {'pet_title':pet_title, 'species': species,'location':location, 
        'tel':tel, 'supplement':supplement, 'photo_url':photo_url,'time':now}
    kv.set(key, value)
    check_location(location)
    kv.disconnect_all()

@app.route('/')
def submit_pet():
    return render_template("index.html")

@app.route('/signin', methods=['GET', 'POST'])
def sign_up():
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')



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