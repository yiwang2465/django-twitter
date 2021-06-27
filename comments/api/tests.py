from testing.testcases import TestCase
from rest_framework.test import APIClient

COMMENT_URL = '/api/comments/'


class CommentApiTest(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create(self):
        # authentication
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)
        # input validation
        response = self.user1_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(COMMENT_URL, {'content': 'some content'})
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['error'], True)

        # success
        response = self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': 'some content-',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'some content')
