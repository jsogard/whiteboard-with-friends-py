import os
import psycopg2
import sqlite3
import urllib
import hashlib
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify, Response

''' ================== '''
'''   CONFIGURATION    '''
''' ================== '''

app = Flask(__name__)
app.config.from_object(__name__)
'''
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
		USERNAME='admin_joe',
		PASSWORD='04161996'
	))
'''
''' ================== '''
'''   AUTHENTICATION   '''
''' ================== '''
'''
def check_auth(username, password):
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
'''
''' ================== '''
'''      DB STUFF      '''
''' ================== '''
'''
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

def populate_db():
	## populates mock data on local ##
	if ON_LOCAL:
		db = get_db()
		with app.open_resource('populate.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

with app.app_context():
	init_db()
	populate_db()
'''
''' ================== '''
'''      ROUTING       '''
''' ================== '''
'''
@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] == '' or request.form['password'] == '':
			error = "Empty fields"
		else:
			pwd = query_select("SELECT password, id FROM User WHERE username=(?) LIMIT 1", (request.form['username'], ) )
			if len(pwd) == 0:
				error = 'Incorrect username'
			else:
				uid = pwd[0]['id']
				pwd = pwd[0]['password']
				m = hashlib.sha256()
				m.update(request.form['password'].encode('utf-8'))
				if pwd != m.hexdigest():
					error = 'Incorrect password'
				else:
					session['logged_in'] = True
					session['id'] = uid
					session['username'] = request.form['username']
					return redirect(url_for('index'))
	return render_template('login.html', error = error)

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('logged_in', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
def signup():
	error = None
	if request.method == 'POST':
		if request.form['username'] == '' or request.form['password'] == '':
			error = 'Empty field'
		elif request.form['password'] != request.form['confirm']:
			error = 'Password does not match'
		else:
			names = query_select("SELECT username FROM User WHERE username=(?) LIMIT 1", (request.form['username'], ) )
			if len(names) > 0:
				error = 'Username taken'
			else:
				m = hashlib.sha256()
				m.update(request.form['password'].encode('utf-8'))
				query_update("INSERT INTO User (username, password) VALUES (?, ?)",
					(request.form['username'], m.hexdigest()))
				session['logged_in'] = True
				session['id'] = uid
				session['username'] = request.form['username']
				return redirect(url_for('index'))
	return render_template('signup.html',  error = error)
'''
@app.route('/', methods=['GET'])
def index():
	#print('you are working on %s' % 'local' if ON_LOCAL else 'heroku')
	if not 'logged_in' in session:
		return redirect(url_for('login'))
	return render_template('dashboard.html')
'''
@app.route('/draw/<int:boardId>', methods=['GET'])
def draw(boardId):
	if not 'logged_in' in session:
		return redirect(url_for('login'))
	# TODO chekc permissions and send away bad guys
	return render_template('draw.html')
'''
''' ================== '''
'''      API ISH       '''
''' ================== '''
'''
@app.route('/user', methods=['GET'])
def getUsers():
	return jsonify(query_select("SELECT * FROM User"))

@app.route('/board', methods=['GET'])
def getBoards():
	if 'logged_in' in session:
		return getUserBoards(session['id'])
	return jsonify(query_select("SELECT * FROM Board"))

@app.route('/board/user/<int:uid>', methods=['GET'])
def getUserBoards(uid):
	return jsonify(query_select("""SELECT b.id, b.name, b.lastModified, u.username
							 FROM Board AS b, User AS u
							 WHERE u.id = (?)
							 AND u.id = b.userId""", (uid,)))

'''
''' ================== '''
'''   HELPER METHODS   '''
''' ================== '''
'''
def query_select(query_str, query_variables=None):
	if ON_LOCAL:
		db = get_db()
		if query_variables == None:
			cur = db.execute(query_str)
		else:	
			cur = db.execute(query_str, query_variables)
		row_list = cur.fetchall()
		data = []
		for row in row_list:
			item = {}
			for key in row.keys():
				item[key] = row[key]
			data.insert(0, item)
		return data

def query_update(query_str, query_variables=None):
	if ON_LOCAL:
		db = get_db()
		if query_variables == None:
			db.execute(query_str)
		else:
			db.execute(query_str, query_variables)
		db.commit()

'''
''' ================== '''
'''   DO NOT TOUCH!!   '''
''' ================== '''

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
