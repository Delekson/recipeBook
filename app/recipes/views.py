"""
Views for Recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipes import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View for manage Recipe APIs
    """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve recipes for authenticated user
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """
        Return serializer class for request
        """
        if self.action == 'list':
            # if we call list endpoint, we use RecipeSerializer
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new recipe
        """
        serializer.save(user=self.request.user)
