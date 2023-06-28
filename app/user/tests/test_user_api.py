"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """
    Helper function which return a user
    """
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """
    Tests the public endpoints in the API
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Testing whether creating a user is successful with pw
        """
        payload = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_create_user_password_not_returned(self):
        """
        Testing whether pw is not in response
        """
        payload = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertNotIn('password', res.data)
        self.assertNotIn(payload['password'], res.data)

    def test_user_with_email_exists_error(self):
        """
        Testing whether error is returned when user w/ email exists
        """
        payload = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        create_user(**payload)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_error(self):
        emails = [
            'name@domain',
            'name@domain.',
            'name@domain.c',
            'name@-domain.com',
            'name@_domain.com',
            'name@domain-.com',
            'name@domain.com_',
            'name@.domain.com',
            'name@domain..com',
            'name@domain@domain.com',
            'name @ domain.com',
            '“”name””@domain.com',
            '“name”@domain@com',
            '“name”@domain”com',
            'verylongname@domain.com_',
            'name@verylongdomainpart.com_',
            ' '
        ]

        loop = 1
        for email in emails:
            payload = {
                'email': email,
                'password': 'testpass12 ',
                'name': 'Test Name ' + str(loop)
            }

            res = self.client.post(CREATE_USER_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

            user_exists = get_user_model().objects.filter(
                email=payload['email']
            ).exists()
            self.assertFalse(user_exists)
            print(str(res.status_code))

    def test_password_too_short_error(self):
        """
        Testing whether error is returned when pw is < 5 char long
        """
        payload = {
            'email': 'name@domain.com',
            'password': 'test',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
