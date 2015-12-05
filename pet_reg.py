from bottle import Bottle, run, route, debug, template, request

application = Bottle()

@application.route('/')
def  pet_register():
	return template("pet_register.tpl")

@application.route('/', method='POST')
def check_information():
	pet_title = request.forms.get('pet-title')
	species = request.forms.get('species')
	location = request.forms.get('location')
	tel = request.forms.get('tel')
	supplement = request.forms.get('supplement')
	
	return template("pet_info_check.tpl",pet_title=pet_title,species=species,location=location,tel=tel,supplement=supplement)



if  __name__ == "__main__":
	application.run(debug=True, reloader=True)