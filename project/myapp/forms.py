from django import forms
from .models import user_profile
from django.forms import ImageField, FileInput

class UserProfileForm(forms.ModelForm):
	image = ImageField(widget=FileInput)
	class Meta:
		model = user_profile
		fields = ['is_2fa_enabled']