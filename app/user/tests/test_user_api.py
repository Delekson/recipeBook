"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_token_for_user(self):
        """
        Testing whether token is generated for valid login
        """
        user_details = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': 'name@domain.com',
            'password': 'testpass123'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_not_exising_creds_error(self):
        """
        Testing whether error is returned with non-existing details
        """
        payload = {
            'email': 'newname@domain.com',
            'password': 'testpass123'
        }

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_bad_email_error(self):
        """
        Testing whether error is return with good pass but bad email
        """
        user_details = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': 'newname@domain.com',
            'password': 'testpass123'
        }

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_bad_password_error(self):
        """
        Testing whether error is return with bad pass but good email
        """
        user_details = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': 'name@domain.com',
            'password': 'testpass1234'
        }

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_email_error(self):
        """
        Testing whether error is returned with blank email & correct pw
        """
        user_details = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': '',
            'password': 'testpass123'
        }

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password_error(self):
        """
        Testing whether error is returned with correct email & blank pw
        """
        user_details = {
            'email': 'name@domain.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': 'name@domain.com',
            'password': ''
        }

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Testing whether authorisation is required for users
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Tests for requests that require authentication
    """
    def setUp(self):
        self.user = create_user(
            email='name@domain.com',
            password='testpass123',
            name='Test Name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Testing whether retrieving profile is successful
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_error(self):
        """
        Test POST to me endpoint is not allowed
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_name_and_password(self):
        """
        Test updating the user name and password for the user
        """
        payload = {
            'name': 'Updated Test Name',
            'password': 'newpass123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
