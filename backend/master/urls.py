from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientMasterViewSet, AllergyMasterViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientMasterViewSet, basename='master-ingredient')
router.register(r'allergies', AllergyMasterViewSet, basename='allergy')

urlpatterns = [
    path('', include(router.urls)),
]
