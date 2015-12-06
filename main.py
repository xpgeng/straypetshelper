# -*- coding: utf-8 -*-
"""
Project: Stray Pets Helper
Author: Shenlang
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
 
import sae, sae.kvdb
#from bottle import Bottle, run, route, debug, template, request
from flask import Flask, request, render_template
from time import strftime, localtime
import os
from werkzeug import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
		pet_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	return render_template("check.html",pet_title = pet_title,
		    species=species, location=location, tel=tel, supplement=supplement)


if  __name__ == "__main__":
	app.run(debug=True)