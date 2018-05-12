from django.urls import path

from . import views

urlpatterns = [
    path('<str:owner>/<int:id>', views.board, name='board'),
	path('gallery/', views.gallery, name='gallery'),
]