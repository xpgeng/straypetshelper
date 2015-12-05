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

app = Flask(__name__)

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
	
	return render_template("check.html",pet_title = pet_title,
		    species=species, location=location, tel=tel, supplement=supplement)


if  __name__ == "__main__":
	app.run(debug=True)