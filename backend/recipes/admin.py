from django.contrib import admin
from .models import Recipe, RecipeIngredient, CookingStep


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class CookingStepInline(admin.TabularInline):
    model = CookingStep
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'cooking_time', 'category', 'source', 'created_at']
    list_filter = ['difficulty', 'category', 'source', 'created_at']
    search_fields = ['title', 'description']
    inlines = [RecipeIngredientInline, CookingStepInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'name', 'master', 'amount']
    search_fields = ['recipe__title', 'name']
    list_filter = ['master__category']


@admin.register(CookingStep)
class CookingStepAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'step_number', 'description', 'time_minutes']
    list_filter = ['recipe']
    ordering = ['recipe', 'step_number']
