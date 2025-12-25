from django.urls import path
from . import views

app_name = 'accounts'

from dj_rest_auth.views import PasswordChangeView

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google/', views.GoogleLogin.as_view(), name='google_login'),
    path('kakao/', views.KakaoLogin.as_view(), name='kakao_login'),
    path('find-id/', views.find_id_view, name='find-id'),
    path('find-password/', views.find_password_view, name='find-password'),
    path('check/', views.check_duplication_view, name='check_duplication'),
    path('password/change/', views.custom_password_change_view, name='rest_password_change'),
]
