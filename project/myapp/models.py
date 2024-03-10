from django.apps import AppConfig
from django.db import models
from django import forms
from django.contrib.auth.models import User

def get_default_user():
    return User.objects.first()

class user_profile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
	login = models.CharField(max_length=100, default='default_value')
	nickname = models.CharField(max_length=100, default='default_value')
	email = models.EmailField(max_length=100, default='default_value')
	last_login = models.DateTimeField(default='2021-01-01 00:00:00')
	is_2fa_enabled = models.BooleanField(default=False)
	def __str__(self):
		return self.login

class PongSpaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
