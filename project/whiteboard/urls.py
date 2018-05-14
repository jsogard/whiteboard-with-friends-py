from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
	path('user/new', views.new_user, name='new_user'),
	path('<str:owner>/<int:id>', views.board, name='board'),
	path('<str:user>', views.user, name='user'),
	path('^$', views.gallery, name='gallery'),
	
]