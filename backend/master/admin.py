from django.contrib import admin
from .models import IngredientMaster, AllergyMaster

@admin.register(IngredientMaster)
class IngredientMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'default_unit', 'icon', 'api_source']
    list_filter = ['category', 'api_source']
    search_fields = ['name']
    ordering = ['name']

@admin.register(AllergyMaster)
class AllergyMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
