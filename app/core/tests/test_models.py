"""
Test models used by Django
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # function retrieves user model


class ModelTests(TestCase):
    """
    Test models
    """

    def test_create_user_with_email_successful(self):
        """
        Check if we can create a user with an email successfully
        """
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """
        Test whether email is normalised for new users
        """
        sample_emails = [
            ['TEST1@example.com', 'TEST1@example.com'],
            ['test2@EXAMPLE.com', 'test2@example.com'],
            ['test3@example.COM', 'test3@example.com'],
            ['tesT4@example.com', 'tesT4@example.com'],
            ['test5@exAMPle.com', 'test5@example.com'],
            ['test6@example.COm', 'test6@example.com'],
            ['tesT7@eXamPle.cOm', 'tesT7@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='password123'
            )
            self.assertEqual(user.email, expected)

    def test_new_user_email_required(self):
        """
        Test whether email is required is prompted when not provided
        """
        with self.assertRaises(ValueError):
            email = ' '
            password = 'testpass123'
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_test_create_superuser(self):
        """
        Check if we can create a superuser successfully
        """
        email = 'admin@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
