from accounts.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.testcases import TestCase


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'


class AccountApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@testing.com',
            password='correct password',
        )

    def test_login(self):
        # all test functions start with test_
        # get is not allowed
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 405)

        # wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # success
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['id'], self.user.id)
        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # log in
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # test login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # get is not allowed
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # success
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # test log out status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # get is not allowed
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # invalid email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # invalid password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # invalid username
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # success
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # user profile
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user=created_user_id).first()
        self.assertNotEqual(profile, None)
        # test login status
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


class UserProfileAPITests(TestCase):

    def test_update(self):
        user1, user1_client = self.create_user_and_client('user1')
        p = user1.profile
        p.nickname = 'old nickname'
        p.save()
        url = USER_PROFILE_DETAIL_URL.format(p.id)

        # test can only be updated by user himself.
        _, user2_client = self.create_user_and_client('user2')
        response = user2_client.put(url, {
            'nickname': 'a new nickname',
        })
        self.assertEqual(response.status_code, 403)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'old nickname')

        # update nickname
        response = user1_client.put(url, {
            'nickname': 'a new nickname',
        })
        self.assertEqual(response.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'a new nickname')

        # update avatar
        response = user1_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        p.refresh_from_db()
        self.assertIsNotNone(p.avatar)
