import unittest
from app.app import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_route_get(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_providers_route(self):
        response = self.client.get("/providers")
        self.assertEqual(response.status_code, 200)

    def test_info_route(self):
        response = self.client.get("/info")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()