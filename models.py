from whiteboard import db

def dump_datetime(value):
	if value is None:
		return None
	return {
		'date'	: value.strftime("%m/%d/%Y"),
		'time'	: value.strftime("%H:%M:%S")
	}

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
	username = db.relationship('Username', backref=db.backref('board'))
	name = db.Column(db.String(64))
	last_modified = db.Column(db.DateTime)
	public = db.Column(db.String(10))

	def __init__(self, user_id, name, last_modified, public):
		self.user_id = user_id
		self.name = name
		self.last_modified = last_modified
		self.public = public

	def __repr__(self):
		return '<Board %r:%r>' % (self.name, self.user_id)

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
		return '<Permission u%r:b%r:%r>' % (self.user_id, self.board_id, self.privilege)

	@property
	def serialize(self):
		return {
			'board'			: self.board.serialize,
			'user'			: self.username.serialize,
			'permission'	: self.privilege
		}