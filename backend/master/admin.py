from django.contrib import admin
from .models import IngredientMaster, IngredientSynonym, AllergyMaster


class IngredientSynonymInline(admin.TabularInline):
    model = IngredientSynonym
    extra = 1


@admin.register(IngredientMaster)
class IngredientMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'default_unit', 'default_storage_method', 'default_expiry_days', 'icon']
    list_filter = ['category', 'default_storage_method']
    search_fields = ['name']
    ordering = ['name']
    inlines = [IngredientSynonymInline]


@admin.register(IngredientSynonym)
class IngredientSynonymAdmin(admin.ModelAdmin):
    list_display = ['synonym', 'master']
    search_fields = ['synonym', 'master__name']


@admin.register(AllergyMaster)
class AllergyMasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
