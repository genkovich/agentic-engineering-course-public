import unittest

from api import pagination


class PaginationTest(unittest.TestCase):
    def test_first_page_without_cursor(self):
        """An empty cursor returns the first page, not an error."""
        rows = pagination.page()
        self.assertEqual(len(rows), pagination.LIMIT)
        self.assertEqual(rows[0]["id"], 1)

    def test_page_after_cursor(self):
        rows = pagination.page(cursor=5)
        self.assertEqual(rows[0]["id"], 6)


if __name__ == "__main__":
    unittest.main()
