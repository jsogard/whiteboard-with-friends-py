from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Board)
admin.site.register(Scheme)