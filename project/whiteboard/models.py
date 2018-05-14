from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=30, primary_key=True)
	password_hash = models.CharField(max_length=64)
	
	def __str__(self):
		return self.username
	
class Board(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	genesis = models.DateField()
	updated = models.DateField()
	
	def __str__(self):
		return { 'owner': self.owner, 'title': self.title, 'id': self.id }