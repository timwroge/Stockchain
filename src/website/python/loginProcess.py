from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('../login.html')

@app.route('/loginProcess', methods=['POST'])
def loginProcess():
	email = request.form['email']
	password = request.form['password']

	if password and email:
		newPassword = password[::-1]
		return jsonify({'password' : newPassword})
	return jsonify({'error' : 'Missing data!'})

if __name__ == '__main__':
	app.run(debug=True)

