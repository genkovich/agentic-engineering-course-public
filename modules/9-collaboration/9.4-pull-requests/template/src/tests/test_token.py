import unittest

from api import token


class TokenTest(unittest.TestCase):
    def test_issue_sets_expiry_in_the_future(self):
        tok = token.issue(7)
        self.assertEqual(tok["user_id"], 7)
        self.assertGreater(tok["expires_at"], token.now())

    def test_fresh_token_is_valid(self):
        self.assertTrue(token.is_valid(token.issue(7)))

    def test_expired_token_is_not_valid(self):
        self.assertFalse(token.is_valid({"expires_at": token.now() - 1}))


if __name__ == "__main__":
    unittest.main()
