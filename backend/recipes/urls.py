from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .chatbot_view import RecipeChatbotView

app_name = 'recipes'

router = DefaultRouter()
router.register(r'', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('chatbot/', RecipeChatbotView.as_view(), name='chatbot'),
    path('', include(router.urls)),
]
