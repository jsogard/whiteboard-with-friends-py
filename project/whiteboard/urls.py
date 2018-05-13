from django.urls import path

from . import views

urlpatterns = [
    path('<str:owner>/<int:id>', views.board, name='board'),
	path('<str:user>', views.user, name='user'),
	path('', views.gallery, name='gallery'),
]