from django.urls import path
from . import views

urlpatterns = [
	path('', views.app),
	path('message', views.handle_message),
]