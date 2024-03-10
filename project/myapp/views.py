from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.template import loader
from .models import user_profile
from . import forms
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserProfileForm
from django.contrib import messages
from django.utils import translation
from django.views.i18n import set_language
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import secrets
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
import pyotp
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

import requests
import json
import os

@permission_classes([IsAuthenticated])
def authenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        user_info = request.session.get('user_info')
        is_2fa_verified = request.session.get('is_2fa_verified', False)

        if user_info and is_2fa_verified:
            return view_func(request, *args, **kwargs)
        else:
            print("not authenticated")
            return redirect('login')

    return wrapper

def login(request):
	user_info = request.session.get('user_info')
	is_2fa_verified = request.session.get('is_2fa_verified', False)
	if user_info and is_2fa_verified:
		return redirect('home')
	print("Login view rendering login.html")
	url = os.environ.get('URL')
	print(f"URL is {url}")
	return render(request, 'login.html', {'user_info': user_info, 'otp_required': False, 'url': url})

@authenticated_user
@permission_classes([IsAuthenticated])
def home(request):
    user_info = request.session.get('user_info')
    is_2fa_verified = request.session.get('is_2fa_verified', False)

    if not is_2fa_verified:
        return redirect('logout_view')

    context = organizer(request)
    return render(request, 'base.html', context)

def organizer(request):
	profile = user_profile.objects.filter(login=request.session['user_info'].get('login')).first()
	if request.method == 'POST':
		is_2fa_enabled_value = request.POST.get('is_2fa_enabled') == 'enable'
		profile.is_2fa_enabled = is_2fa_enabled_value
		profile.save()
		return redirect('edit')
	return {
		'user': profile,
	}


@authenticated_user
@permission_classes([IsAuthenticated])
def doubles(request):
	return render(request, 'doubles.html')

@authenticated_user
@permission_classes([IsAuthenticated])
def game(request):
    is_home_page = False
    is_game = True
    return render(request, 'game.html', {'is_home_page': is_home_page, 'is_game': is_game})

@authenticated_user
@permission_classes([IsAuthenticated])
def pong(request):
	return render(request, 'pong.html')

def authorize(request):
    client_id = os.environ.get('CLIENT_ID2')
    redirect_uri = f"https://{request.get_host()}/callback"

    authorization_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri=https://10.13.1.14:8000/callback&response_type=code"

    return redirect('/home/')

@authenticated_user
@permission_classes([IsAuthenticated])
def logout_view(request):
	logout(request)
	response = redirect('login')  # Redirect to login page after logout
	response.delete_cookie('sessionid')  # Delete sessionid cookie
	response.delete_cookie('csrftoken')  # Delete csrftoken cookie
	request.session.flush()
	request.session.clear()  # Clear session data
	request.session['is_2fa_verified'] = False
	return response

@authenticated_user
@permission_classes([IsAuthenticated])
def tournament(request):
	return render(request, 'tournament.html')


@authenticated_user
@permission_classes([IsAuthenticated])
def edit(request):
	is_game = False
	is_home_page = False
	profile = user_profile.objects.filter(login=request.session['user_info'].get('login')).first()
	user_info = request.session.get('user_info')
	is_2fa_verified = request.session.get('is_2fa_verified', False)

	if not is_2fa_verified:
		return redirect('logout_view')

	if request.method == 'POST':
		is_2fa_enabled_value = request.POST.get('is_2fa_enabled') == 'enable'
		profile.is_2fa_enabled = is_2fa_enabled_value
		profile.save()
		messages.success(request, "data saved")
		return redirect('edit')
	tmp = organizer(request)
	context = {
		'user': profile,
	}
	return render(request, 'base.html', context)



def verify_2fa(request):
	if request.method == 'POST':
		otp = request.POST.get('otp')
		print (f"otp is {otp}")
		username = request.session['user_info'].get('login')
		user = user_profile.objects.get(login=username)

		otp_secret = request.session['otp_secret_key']
		otp_valid_until = request.session['otp_valid_until']

		if otp_secret and otp_valid_until is not None:
			otp_valid_until = datetime.fromisoformat(otp_valid_until)

			if otp_valid_until > datetime.now():
				totp = pyotp.TOTP(otp_secret, interval=300)
				if totp.verify(otp):
					auth_login(request, user)

					del request.session['otp_secret_key']
					del request.session['otp_valid_until']

					request.session['is_2fa_verified'] = True

					return redirect('home')
				else:
					messages.error(request, 'Invalid code')
					logout(request)
					print("Invalid codeddddddddddddd")
					return redirect('logout_view')
			else:
				messages.error(request, 'Code expired')
				return redirect('logout_view')
		else:
			messages.error(request, 'Session data missing')
			return redirect('logout_view')
	else:
		return render(request, 'error.html', {'error': 'Invalid request method'})

