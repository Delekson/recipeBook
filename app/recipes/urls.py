"""
URL mapping for the recipe app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipes import views


router = DefaultRouter()
router.register('recipe', views.RecipeViewSet)

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls))
]
