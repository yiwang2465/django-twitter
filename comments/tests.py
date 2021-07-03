from testing.testcases import TestCase


class CommentModelTest(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.tweet1 = self.create_tweet(self.user1, 'come tweet')
        self.comment1 = self.create_comment(self.user1, self.tweet1, 'good one')

    def test_comment(self):
        self.assertNotEqual(self.comment1.__str__, None)

    def test_like_set(self):
        self.create_like(self.user1, self.comment1)
        self.assertEqual(self.comment1.like_set.count(), 1)

        self.create_like(self.user1, self.comment1)
        self.assertEqual(self.comment1.like_set.count(), 1)

        user2 = self.create_user('user2')
        self.create_like(user2, self.comment1)
        self.assertEqual(self.comment1.like_set.count(), 2)
