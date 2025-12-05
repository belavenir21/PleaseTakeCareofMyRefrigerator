from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recipes'

router = DefaultRouter()
router.register(r'', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
