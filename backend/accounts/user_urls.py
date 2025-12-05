from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('me/', views.user_detail_view, name='user-detail'),
    path('me/profile/', views.user_profile_update_view, name='profile-update'),
]
