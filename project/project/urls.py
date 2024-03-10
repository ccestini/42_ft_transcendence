from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import home
from myapp.views import game
from myapp.views import verify_2fa
from myapp.views import authorize
from myapp.aouth import callback
from django.conf.urls.i18n import i18n_patterns
from myapp.views import logout_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('game/', game),
    path('authorize/', authorize, name='authorize'),
    path('callback/', callback, name='callback'),
    path('debug/', include('debug_toolbar.urls')),
    path('logout/', logout_view, name='logout_view'),
	path('verify_2fa/', verify_2fa, name='verify_2fa'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)