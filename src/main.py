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
from flask import Flask, request, render_template, url_for, send_from_directory
from time import strftime, localtime
from werkzeug import secure_filename
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey

monkey.patch_all()

#####################constant variable######################
ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = ROOT+'/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def check_filename(filename):
    if filename in ALLOWED_EXTENSIONS:
        filename_new = "%s.%s" % (int(time.time()), filename)
        return filename_new
    else:
        return filename


def save_image(filename, file):
    c = Connection()
    bucket = c.get_bucket('imges')
    bucket.put_object(filename, file.read())
    print bucket.generate_url(filename) 
    return bucket.generate_url(filename)

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
        print renew_filename
        pet_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], renew_filename))
        save_image(renew_filename, pet_photo)

    return render_template("check.html", pet_title=pet_title,
            species=species, location=location, tel=tel, supplement=supplement)


if  __name__ == "__main__":
	app.run(debug=True)