import os
import psycopg2
import sqlite3
import urllib
import hashlib
from flask import Flask, render_template, request, redirect, url_for, g, session

''' ================== '''
'''   CONFIGURATION    '''
''' ================== '''

app = Flask(__name__)
app.config.from_object(__name__)

ON_LOCAL = ('DATABASE_URL' not in os.environ)

if not ON_LOCAL:
	#urlparse.uses_netloc.append("postgres")
	url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
	url.netloc += "postgres" # ?? does this work ?? not it does not
	conn = psycopg2.connect(
		database=url.path[1:],
		user=url.username,
		password=url.password,
		host=url.hostname,
		port=url.port
	)
else:
	app.config.update(dict(
		DATABASE=os.path.join(app.root_path, 'whiteboard.db'),
		SECRET_KEY='development key',
		USERNAME='admin',
		PASSWORD='default'
	))

with app.app_context():
	init_db()

''' ================== '''
'''      DB STUFF      '''
''' ================== '''

def connect_db():
	## connects to specified database ##
	if ON_LOCAL:
		rv = sqlite3.connect(app.config['DATABASE'])
		rv.row_factory = sqlite3.Row
		return rv

def get_db():
	## opens new db conn if none yet ##
	if ON_LOCAL:
		if not hasattr(g, 'sqlite_db'):
			g.sqlite_db = connect_db()
		return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	## closes database when on local ##
	if ON_LOCAL and hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	## initializes db on local ##
	if ON_LOCAL:
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()


''' ================== '''
'''      API ISH       '''
''' ================== '''

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
	print('you are working on %s' % 'local' if ON_LOCAL else 'heroku')
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('index.html')

''' ================== '''
'''   HELPER METHODS   '''
''' ================== '''

def query_select(query_str, query_variables):
	if ON_LOCAL:
		db = get_db()
		cur = db.execute(query_str, query_variables)
		row_list = cur.fetchall()
		data = []
		for row in row_list:
			item = {}
			for key in row.keys():
				item[key] = row[key]
			data.insert(0, item)
		print data
		return data


''' ================== '''
'''   DO NOT TOUCH!!   '''
''' ================== '''

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
