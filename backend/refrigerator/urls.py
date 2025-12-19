from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'refrigerator'

router = DefaultRouter()
router.register('ingredients', views.UserIngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
