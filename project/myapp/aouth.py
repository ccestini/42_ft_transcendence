import requests
from django.shortcuts import render
from django.http import HttpResponseServerError
from .models import user_profile
from django.contrib.auth import login
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from email.mime.text import MIMEText
from django.conf import settings
import smtplib
import pyotp
from datetime import datetime, timedelta
import os
from rest_framework_simplejwt.tokens import RefreshToken

def send_message_to_email(user, otp):
	msg = MIMEText(f'Code of confirmation 2FA: {otp}')
	msg['Subject'] = "Confirmation 2FA"
	msg['From'] = settings.EMAIL_HOST_USER 
	msg['To'] = user.email

	mail = smtplib.SMTP(settings.EMAIL_HOST, 587)
	mail.starttls()
	mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
	mail.sendmail(settings.EMAIL_HOST_USER, user.email, msg.as_string())
	mail.quit()
    
def create_otp(request):
     totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
     otp = totp.now()
     request.session['otp_secret_key'] = totp.secret
     valid_until = datetime.now() + timedelta(seconds=300)
     request.session['otp_valid_until'] = str(valid_until)
     return otp

    

def callback(request):
	if 'code' in request.GET:
		code = request.GET.get('code')
		print(f"Received authorization code: {code}")

		token_url = os.environ.get('TOKEN_URL')
		client_id = os.environ.get('CLIENT_ID')
		client_secret = os.environ.get('CLIENT_SECRET')
		redirect_uri = os.environ.get('REDIRECT_URI')

		data = {
			'grant_type': 'authorization_code',
			'client_id': client_id,
			'client_secret': client_secret,
			'code': code,
			'redirect_uri': redirect_uri,
		}

		try:
			response = requests.post(token_url, data=data)
			response.raise_for_status()
			token_data = response.json()

			if 'access_token' in token_data:
				token = token_data['access_token']

				user_info_url = os.environ.get('USER_INFO_URL')
				headers = {'Authorization': f'Bearer {token}'}
				user_response = requests.get(user_info_url, headers=headers)
				user_response.raise_for_status()
				user_info = user_response.json()

				user_instance, created = User.objects.get_or_create(username=user_info.get('login'))

				refresh = RefreshToken.for_user(user_instance)
				access_token = str(refresh.access_token)
				print(f' ACCESS TOKEN JWT {access_token}')

				request.session['access_token'] = access_token
				request.session['is_2fa_verified'] = True

				if not user_profile.objects.filter(login=user_info.get('login')).exists():
					user_instance, created = User.objects.get_or_create(username=user_info.get('login'))
					user_profile.objects.create(
						user=user_instance,
						login=user_info.get('login'),
						nickname=user_info.get('displayname'),
						email=user_info.get('email'),
					).save()
					request.session['user_info'] = user_info
					return render(request, 'home.html', {'user_info': user_info})

				user = user_profile.objects.get(login=user_info.get('login'))

				if user.is_2fa_enabled:
					
					otp = create_otp(request)
					
					send_message_to_email(user, otp)
					
					request.session['is_2fa_verified'] = False
					
					request.session['user_info'] = user_info
					
					return render(request, 'login.html', {'user_info': user_info, 'otp_required': True})
				else:
					request.session['is_2fa_verified'] = True
					request.session['user_info'] = user_info
					login(request, user.user)
					return render(request, 'home.html', {'user_info': user_info})
			else:
				return render(request, 'error.html', {'error': 'Access token not found in the response'})
		except requests.exceptions.RequestException as e:
			return HttpResponseServerError(f"An error occurred: {e}")
	else:
		return render(request, 'error.html', {'error': 'Authorization code is missing'})
