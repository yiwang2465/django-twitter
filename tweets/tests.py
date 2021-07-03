from datetime import timedelta
from testing.testcases import TestCase
from utils.time_helpers import utc_now


class TweetTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.tweet1 = self.create_tweet(self.user1, content='new tweet')

    def test_hours_to_now(self):
        self.tweet1.created_at = utc_now() - timedelta(hours=10)
        self.tweet1.save()
        self.assertEqual(self.tweet1.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(user=self.user1, target=self.tweet1)
        self.assertEqual(self.tweet1.like_set.count(), 1)

        self.create_like(self.user1, self.tweet1)
        self.assertEqual(self.tweet1.like_set.count(), 1)

        user2 = self.create_user('user2')
        self.create_like(user2, self.tweet1)
        self.assertEqual(self.tweet1.like_set.count(), 2)
