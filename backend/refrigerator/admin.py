from django.contrib import admin
from .models import UserIngredient


@admin.register(UserIngredient)
class UserIngredientAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'master', 'quantity', 'unit', 'storage_method', 'expiry_date', 'is_deleted']
    list_filter = ['storage_method', 'is_deleted', 'expiry_date']
    search_fields = ['name', 'user__username', 'master__name']
    ordering = ['expiry_date', 'name']
    date_hierarchy = 'expiry_date'
