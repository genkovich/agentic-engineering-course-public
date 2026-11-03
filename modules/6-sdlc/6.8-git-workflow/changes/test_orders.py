import unittest

from api import orders


class OrdersListTest(unittest.TestCase):
    def test_first_page_without_cursor(self):
        rows = orders.list_orders()
        self.assertTrue(rows)
        self.assertEqual(rows[0]["id"], 1)

    def test_page_after_cursor(self):
        rows = orders.list_orders(cursor=5)
        self.assertEqual(rows[0]["id"], 6)


if __name__ == "__main__":
    unittest.main()
