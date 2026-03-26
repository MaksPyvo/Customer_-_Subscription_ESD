import unittest
from unittest.mock import patch, MagicMock
from app.app import app


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch("app.app.Customer")
    def test_login_success(self, mock_customer_model):
        mock_customer = MagicMock()
        mock_customer.mobile = "5195558691"
        mock_customer_model.query.filter_by.return_value.first.return_value = mock_customer

        response = self.client.post("/login", json={
            "username": "I985",
            "password": "5195558691"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("Login successful", response.get_data(as_text=True))

    @patch("app.app.Customer")
    def test_login_invalid_mobile(self, mock_customer_model):
        mock_customer = MagicMock()
        mock_customer.mobile = "5195550000"
        mock_customer_model.query.filter_by.return_value.first.return_value = mock_customer

        response = self.client.post("/login", json={
            "username": "I985",
            "password": "5195558691"
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_data(as_text=True))

    @patch("app.app.Customer")
    def test_login_unknown_user(self, mock_customer_model):
        mock_customer_model.query.filter_by.return_value.first.return_value = None

        response = self.client.post("/login", json={
            "username": "X999",
            "password": "1234567890"
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()