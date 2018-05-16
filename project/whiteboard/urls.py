from django.urls import path

from . import views

urlpatterns = [
	path('user/new', views.new_user, name='new_user'),
	path('login', views.login, name='login'),
	path('logout', views.logout, name='logout'),
	path('<str:owner>/<int:id>', views.board, name='board'),
	path('<str:user>', views.user, name='user'),
	path('', views.gallery, name='gallery'),
	
]