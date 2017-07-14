import os
import psycopg2
import urllib
from flask import Flask, render_template, request, redirect, url_for, g, session

app = Flask(__name__)
app.config.from_object(__name__)

ON_LOCAL = ('DATABASE_URL' not in os.environ)

if not ON_LOCAL:
	#urlparse.uses_netloc.append("postgres")
	url = urllib.parse(os.environ["DATABASE_URL"])
	url.netloc += "postgres" # ?? does this work ??
	conn = psycopg2.connect(
		database=url.path[1:],
		user=url.username,
		password=url.password,
		host=url.hostname,
		port=url.port
	)
else:
	app.config.update(dict(
		DATABASE=os.path.join(app.root_path, 'app.db'),
		SECRET_KEY='development key',
		USERNAME='admin',
		PASSWORD='default'
	))

@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			session['logged_in'] = True
			return redirect(url_for('index'))
		error = "Invalid username or password"
	return render_template('login.html', error = error)

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def index():
	#print('you are working on %s' % 'local' if ON_LOCAL else 'heroku')
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('index.html')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
