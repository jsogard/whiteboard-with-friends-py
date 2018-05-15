from django.db import models
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
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	genesis = models.DateField()
	updated = models.DateField()
	
	def __str__(self):
		return { 'owner': self.owner, 'title': self.title, 'id': self.id }