from flask import *
import os

app = Flask(__name__)

def getListOfAliases():
        f = []
        dirs = os.listdir("sounds/")
        for file in dirs:
                f.append(file[:file.rfind('.')])
        return f

@app.route("/", methods=['POST', 'GET'])
def hello():
	error = None
	buttonLabels = getListOfAliases()
	if request.method == 'POST':
		print(request.form['label'])
		play_sound(request.form['label'])
	return render_template('index.html', buttonLabels=buttonLabels)
