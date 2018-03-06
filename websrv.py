from flask import *
import os

app = Flask(__name__)

def getListOfAliases():
	f = []
	dirs = os.listdir("sounds/")
	for file in dirs:
		f.append(file[:file.rfind('.')])
	f.sort()
	return f

@app.route("/", methods=['POST', 'GET'])
def requ():
	error = None
	buttonLabels = getListOfAliases()
	if request.method == 'POST':
		if "label" in request.form:
			print(request.form['label'])
			play_sound(request.form['label'])
		elif "volume" in request.form:
			print(request.form['volume'])
			set_volume(request.form['volume'])
	return render_template('index.html', buttonLabels=buttonLabels)
