from django.db import models
from django.utils.timezone import now
from datetime import datetime
import hashlib

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=30, unique=True)
	password_hash = models.CharField(max_length=64)
	
	def __str__(self):
		return self.username
	
	def crypto(self, password):
		# password_hash = sha256(sha256(password) + sha256(username))
		salt = hashlib.sha256()
		salt.update(self.username.encode('UTF-8'))
		pwd = hashlib.sha256()
		pwd.update(password.encode('UTF-8'))
		pwd.update(salt.digest())
		return pwd.hexdigest()
		
		
	
class Board(models.Model):
	owner = models.ForeignKey('User', on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	genesis = models.DateTimeField(default=datetime.now(), blank=True)
	updated = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return str.format('{}: \"{}\" by @{}', self.id, self.title, self.owner.username)
	
class Scheme(models.Model):
	name = models.CharField(max_length=30, unique=True)
	background = models.CharField(max_length=60)
	frame = models.CharField(max_length=60)
	border = models.CharField(max_length=60)
	text = models.CharField(max_length=60)
	accent = models.CharField(max_length=60)
	
	def __str__(self):
		return self.name
	
	def peek(self):
		return { 'frame': self.frame, 'border': self.border }
	