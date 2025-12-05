from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nickname', 'diet_goals', 'created_at']
    search_fields = ['user__username', 'nickname']
    list_filter = ['created_at']
