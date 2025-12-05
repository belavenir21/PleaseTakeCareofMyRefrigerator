from django.contrib import admin
from .models import UserIngredient

@admin.register(UserIngredient)
class UserIngredientAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'quantity', 'unit', 'storage_method', 'expiry_date', 'is_expiring_soon']
    list_filter = ['storage_method', 'unit', 'expiry_date']
    search_fields = ['name', 'user__username']
    ordering = ['expiry_date', 'name']
    date_hierarchy = 'expiry_date'
