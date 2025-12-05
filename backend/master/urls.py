from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientMasterViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientMasterViewSet, basename='master-ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
