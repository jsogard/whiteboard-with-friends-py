# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash
import hashlib

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file , wwf.py

# Load default config and override config from an environment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='admin'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database."""
	init_db()
	print('Initialized the database.')

@app.route('/dashboard')
def dashboard():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('dashboard.html', entries=entries)

@app.route('/', methods=['GET', 'POST'])
def login():
	if 'logged_in' in session.keys() and session['logged_in']:
		return redirect(url_for('dashboard'))
	error = None
	if request.method == 'POST':
		if request.form['username'] not in app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('dashboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	error = None
	if request.method == 'POST':
		# validate passwords match
		if request.form['password'] != request.form['confirm']:
			error = 'Passwords do not match'
			return render_template('signup.html', error=error)

		db = get_db()
		uname = request.form['username']

		# validate username
		def validate_username(uname):
			validc = 'qwertyuiopasdfghjklzxcvbnm.1234567890!@#$%&_-?|'
			for c in uname:
				if c not in validc:
					return False
			return True
		if not validate_username(uname):
			error = 'Invalid characters in unsername'
			return render_template('signup.html', error=error)

		# query db for duplicate username
		cur = db.execute("SELECT COUNT(1) FROM User WHERE username = ?", (uname,))
		if cur.fetchone() == None:
			# the username does not already exist
			h = hashlib.new('sha256')
			h.update(request.form['password'].encode('utf-8'))
			db.execute("INSERT INTO User (username, password) VALUES (?, ?)", (uname, h.hexdigest()) )
			session['logged_in'] = True
			return redirect(url_for('dashboard'))
		error = 'Username already taken'
	return render_template('signup.html', error=error)

# TODO require auth
@app.route('/users', methods=['GET'])
def get_all_users():
	db = get_db()
	res = db.execute('SELECT * FROM User')
	return res.fetchall()

@app.route('/users/{uid}', methods=['GET'])
def get_user(uid):
	db = get_db()
	if type(uid) is str:
		res = db.execute('SELECT * FROM User WHERE username=?', (uid,))
	elif type(uid) is int:
		res = db.execute('SELECT * FROM User WHERE id=?', (uid,))
	else:
		return 400
	return res