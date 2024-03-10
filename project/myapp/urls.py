from django.urls import include, path
from . import views
from django.urls import include, path


urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('game/', views.game, name='game'),
    path('pong', views.pong, name='pong'),
    path('profile/', views.edit, name='edit'),
    path('profile/edit', views.edit, name='edit'),
    path('logout/', views.logout_view, name='logout_view'),
    path('verify_2fa/', views.verify_2fa, name='verify_2fa'),
	path('doubles/', views.doubles, name='doubles'),
	path('tournament/', views.tournament, name='tournament'),
]
