import os
import psycopg2
import sqlite3
import urllib
import hashlib
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

''' ================== '''
'''   CONFIGURATION    '''
''' ================== '''

app = Flask(__name__)
app.config.from_object(__name__)

## make True if working in test
ON_LOCAL = False
if not ON_LOCAL:
	## reached when deployed to heroku
	if 'DATABASE_URL' in os.environ:
		DBURI = os.environ['DATABASE_URL']
	## reached when using postgress db in dev
	## ERRORS IF DB_URI HAS NOT BEEN UPDATED from https://data.heroku.com/datastores/09317768-cb46-4413-8f70-4000e5fdc9ed
	## cli with heroku pg:psql postgresql-acute-28574 --app whiteboard-with-friends-py
	else:
		with app.open_resource('db_uri.txt', mode='r') as f:
			DBURI = f.read()

	app.config['SQLALCHEMY_DATABASE_URI'] = DBURI
	db = SQLAlchemy(app)
	url = urllib.parse.urlparse(DBURI)

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

''' ================== '''
'''   AUTHENTICATION   '''
''' ================== '''

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

''' ================== '''
'''      DB MODELS     '''
''' ================== '''

class Username(db.Model):
	__tablename__ = 'username'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True)
	password = db.Column(db.String(64))

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User %r>' % self.username

	@property
	def serialize(self):
		return {
			'id'		: self.id,
			'username'	: self.username
		}

class Board(db.Model):
	__tablename__ = 'board'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('username.id'))
	username = db.relationship('Username', backref=db.backref('board')) # ??
	name = db.Column(db.String(64))
	last_modified = db.Column(db.DateTime)
	public = db.Column(db.String(10))

	def __init__(self, user_id, name, last_modified, public):
		self.user_id = user_id
		self.name = name
		self.last_modified = last_modified
		self.public = public

	def __repr__(self):
		return '<Board %r:%r>' % (name, user_id) ## check the wildcard

	@property
	def serialize(self):
		return {
			'id'			: self.id,
			'user'			: self.username.serialize,
			'name'			: self.name,
			'last_modified'	: dump_datetime(self.last_modified),
			'public'		: self.public
		}

class Permission(db.Model):
	__tablename__ = 'permission'

	board_id = db.Column(db.Integer, db.ForeignKey('board.id'), primary_key=True)
	board = db.relationship('Board', backref=db.backref('permission'))
	user_id = db.Column(db.Integer, db.ForeignKey('username.id'), primary_key=True)
	username = db.relationship('Username', backref=db.backref('permission'))
	privilege = db.Column(db.String(10), primary_key=True)

	def __init__(self, board_id, user_id, privilege):
		self.board_id = board_id
		self.user_id = user_id
		self.privilege = privilege

	def __repr__(self):
		return '<Permission >'

	@property
	def serialize(self):
		return {
			'board'			: self.board.serialize,
			'user'			: self.username.serialize,
			'permission'	: self.privilege
		}


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

''' ================== '''
'''      ROUTING       '''
''' ================== '''

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

@app.route('/', methods=['GET'])
def index():
	#print('you are working on %s' % 'local' if ON_LOCAL else 'heroku')
	if not 'logged_in' in session:
		return redirect(url_for('login'))
	return render_template('dashboard.html')

@app.route('/draw/<int:boardId>', methods=['GET'])
def draw(boardId):
	if not 'logged_in' in session:
		return redirect(url_for('login'))
	# TODO chekc permissions and send away bad guys
	return render_template('draw.html')

''' ================== '''
'''      API ISH       '''
''' ================== '''

@app.route('/user', methods=['GET'])
def getUsers():
	if ON_LOCAL:
		return jsonify(query_select("SELECT * FROM User"))
	else:
		return jsonify(json_list=[i.serialize for i in Username.query.all()])

@app.route('/board', methods=['GET','POST'])
def getBoards():
	if request.method == 'GET': # get all boards
		if 'logged_in' in session:
			return getUserBoards(session['id'])
		if ON_LOCAL:
			return jsonify(query_select("SELECT * FROM Board"))
		else:
			return jsonify(json_list=[i.serialize for i in Board.query.all()])
	
	elif request.method == 'POST': # create new board
		board_json = json.loads(request.data)
		board = Board(user_id = session['id'] if 'id' in session else board_json['id'],
					  name = board_json['name'],
					  public = board_json['public'],
					  last_modified = 'NOW()')
		db.session.add(board)
		db.session.commit()
		return jsonify(board.serialize)


@app.route('/board/user/<int:uid>', methods=['GET'])
def getUserBoards(uid):
	if ON_LOCAL:
		return jsonify(query_select("""SELECT b.id, b.name, b.lastModified, u.username
								 FROM Board AS b, User AS u
								 WHERE u.id = (?)
								 AND u.id = b.userId""", (uid,)))
	return jsonify(json_list=[i.serialize for i in Board.query.filter(Board.user_id==uid).all()])

@app.route('/permission', methods=['GET'])
def getAllPermissions():
	if ON_LOCAL:
		return None ## TODO
	else:
		return jsonify(json_list=[i.serialize for i in Permission.query.all()])

@app.route('/permission/user/<int:uid>', methods=['GET'])
def getPermittedBoards(uid):
	if ON_LOCAL:
		return None ## TODO

	## check boards that admin has full permissions on ##
	delete_boards = []

	delete_boards.extend(
		[i.serialize for i in Board.query.filter(Board.user_id==uid).all()]
	) # boards user owns
	delete_boards.extend(
		[i.board.serialize for i in Permission.query.filter(Permission.privilege=='DELETE',Permission.user_id==uid).all()]
	) # user has been given full privilege
	print(jsonify(delete_boards))

	## check boards that admin has only write permissions on ##
	write_boards = []

	write_boards.extend(
		[i.serialize for i in Board.query.filter(Board.public=='WRITE').all() if i.serialize]
	) # public write boards
	write_boards.extend(
		[i.board.serialize for i in Permission.query.filter(Permission.privilege=='WRITE',Permission.user_id==uid).all()]
	) # user has been given write privilege
	print(jsonify(write_boards))

	#write_boards = [i for i in write_boards not in delete_boards]

	## check boards that admin has only read permissions on ##
	read_boards = []
	read_boards.extend(
		[i.serialize for i in Board.query.filter(Board.public=='READ').all()]
	) # public read boards
	read_boards.extend(
		[i.serialize for i in Permission.query.filter(Permission.privilege=='READ',Permission.user_id==uid).all()]
	) #user has bee given read privilege
	print(jsonify(write_boards))

	#read_boards = [i for i in read_boards not in delete_boards not in write_boards]

	return jsonify({'delete': delete_boards, 'write': write_boards, 'read':read_boards})
	


''' ================== '''
'''   HELPER METHODS   '''
''' ================== '''

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

def dump_datetime(value):
	if value is None:
		return None
	return {
		'date'	: value.strftime("%m/%d/%Y"),
		'time'	: value.strftime("%H:%M:%S")
	}

''' ================== '''
'''   DO NOT TOUCH!!   '''
''' ================== '''

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
