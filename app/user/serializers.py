"""
Serializers for the user API view
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

from email_validator import validate_email


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object
    """

    class Meta:  # tells rest_framework what to parse to serializer
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,  # can only write vals to parser not read
                'min_length': 5
            }
        }

    def validate_email(self, value):
        try:
            validate_email(value)
            return value
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        """
        Create and return a user with an encrypted pw
        """
        return get_user_model().objects.create_user(**validated_data)
