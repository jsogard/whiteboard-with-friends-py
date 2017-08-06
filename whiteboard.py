import os
import psycopg2
import sqlite3
import urllib
import hashlib
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
#from models import Username, Board, Permission
import models


SQLALCHEMY_TRACK_MODIFICATIONS = False

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
		return jsonify(json_list=[i.serialize for i in models.Username.query.all()])

@app.route('/board', methods=['GET','POST'])
def getBoards():
	if request.method == 'GET': # get all boards
		if 'logged_in' in session:
			return getUserBoards(session['id'])
		if ON_LOCAL:
			return jsonify(query_select("SELECT * FROM Board"))
		else:
			return jsonify(json_list=[i.serialize for i in models.Board.query.all()])
	
	elif request.method == 'POST': # create new board
		board_json = json.loads(request.data)
		board = models.Board(user_id = session['id'] if 'id' in session else board_json['id'],
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
	return jsonify(json_list=[i.serialize for i in models.Board.query.filter(models.Board.user_id==uid).all()])

@app.route('/permission', methods=['GET', 'PUT'])
def getAllPermissions():
	if request.method == 'GET':
		if ON_LOCAL:
			return None ## TODO
		else:
			return jsonify(json_list=[i.serialize for i in models.Permission.query.all()])
	
	elif request.method == 'PUT':
		'''
		Add new permission
		{
			"board_id": X,
			"user_id": X,
			"privilege": 'XXXX'
		}
		'''
		if ON_LOCAL:
			return None
		perm_json = json.loads(request.data)
		perm_board = models.Board.query.filter(models.Board.id == perm_json['board_id']).first()
		
		## TODO fix all this shit. weird logic to figure out
		if perm_board.public != 'RESTRICT' and privilege_cmp(perm_json['privilege'],perm_board.public) <= 0:
			return jsonify(error="User already has %r permissions" % perm_json['privilege']), 403
		
		try:
			perm = models.Permission(board_id = perm_json['board_id'],
									 user_id = perm_json['user_id'],
									 privilege = perm_json['privilege'])
			db.session.add(perm)
			db.session.commit()
		except Exception as e:
			return jsonify(error="Board already %r by default" % perm_board.public), 403
		
		return jsonify(perm.serialize)

@app.route('/permission/user/<int:uid>', methods=['GET'])
def getPermittedBoards(uid):
	if ON_LOCAL:
		return None ## TODO

	restrict = get_restrict_boards(uid)

	delete = get_delete_boards(uid)
	delete = list(filter(lambda board: board not in restrict, delete))

	write = get_write_boards(uid)
	write = list(filter(lambda board: board not in restrict, write))
	write = list(filter(lambda board: board not in delete, write))

	read = get_read_boards(uid)
	read = list(filter(lambda board: board not in restrict, read))
	read = list(filter(lambda board: board not in delete, read))
	read = list(filter(lambda board: board not in write, read))

	all_boards = []
	if delete:
		for i in delete:
			i['privilege'] = 'DELETE'
		all_boards.extend(delete)
	if write:
		for i in write:
			i['privilege'] = 'WRITE'
		all_boards.extend(write)
	if read:
		for i in read:
			i['privilege'] = 'READ'
		all_boards.extend(read)

	return jsonify(boards=all_boards)
	


''' ================== '''
'''   HELPER METHODS   '''
''' ================== '''

def get_delete_boards(user_id):
	## check boards that admin has full permissions on ##
	delete_boards = []

	delete_boards.extend(
		[i.serialize for i in models.Board.query.filter(models.Board.user_id==user_id)
												.all()]
	) # boards user owns
	delete_boards.extend(
		[i.board.serialize for i in models.Permission.query.filter(models.Permission.privilege=='DELETE',
																   models.Permission.user_id==user_id)
														   .all()]
	) # user has been given full privilege

	return sorted(delete_boards, key=lambda board: board['id'])

def get_write_boards(user_id):
	## check boards that admin has only write permissions on ##
	write_boards = []

	write_boards.extend(
		[i.serialize for i in models.Board.query.filter(models.Board.public=='WRITE').all()]
	) # public write boards
	write_boards.extend(
		[i.board.serialize for i in models.Permission.query.filter(models.Permission.privilege=='WRITE',models.Permission.user_id==user_id).all()]
	) # user has been given write privilege
	
	return sorted(write_boards, key=lambda board: board['id'])

def get_read_boards(user_id):
	## check boards that admin has only read permissions on ##
	read_boards = []

	read_boards.extend(
		[i.serialize for i in models.Board.query.filter(models.Board.public=='READ').all()]
	) # public read boards
	read_boards.extend(
		[i.serialize for i in models.Permission.query.filter(models.Permission.privilege=='READ',models.Permission.user_id==user_id).all()]
	) #user has bee given read privilege

	return sorted(read_boards, key=lambda board: board['id'])

def get_restrict_boards(user_id):
	return [i.board.serialize for i in models.Permission.query.filter(models.Permission.privilege=='RESTRICT', models.Permission.user_id==user_id).all()]

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

## returns negative if priv1 is more restrictive than priv2
def privilege_cmp(priv1, priv2):
	cmp_dict = {
		'RESTRICT':	0,
		'READ':		1,
		'WRITE':	2,
		'DELETE':	3
	}
	return cmp_dict[priv1] - cmp_dict[priv2]

''' ================== '''
'''   DO NOT TOUCH!!   '''
''' ================== '''

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
