import unittest
from unittest.mock import patch, MagicMock
from app.app import app


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # connect generate token and customer models
    @patch("app.app.generate_token")
    @patch("app.app.Customer")
    def test_login_success_json(self, mock_customer_model, mock_generate_token):
        # setup Mocks
        mock_customer = MagicMock()
        
        mock_customer.client_id = "X009"
        mock_customer.mobile = "5195556338"
        mock_customer_model.query.filter_by.return_value.first.return_value = mock_customer
        
        # mock token generation
        fake_token = "mocked.jwt.token"
        mock_generate_token.return_value = fake_token

        # execute Request
        response = self.client.post("/login", json={
            "username": "X009",
            "password": "5195556338"
        })

        # assert
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check JSON response body
        response_json = response.get_json()
        self.assertEqual(response_json["message"], "Login successful")
        self.assertEqual(response_json["token"], fake_token)
        
        # Check Authorization Header
        self.assertEqual(response.headers.get("Authorization"), f"Bearer {fake_token}")
        
        # Check Cookies
        cookies = response.headers.getlist('Set-Cookie')
        cookie_found = any(f'jwt_token={fake_token}' in cookie for cookie in cookies)
        self.assertTrue(cookie_found, "jwt_token cookie was not set correctly")
        
    @patch("app.app.generate_token")
    @patch("app.app.Customer")
    def test_login_success_form(self, mock_customer_model, mock_generate_token):
        # setup Mocks
        mock_customer = MagicMock()
        mock_customer.client_id = "X009"
        mock_customer.mobile = "5195556338"
        mock_customer_model.query.filter_by.return_value.first.return_value = mock_customer
        
        fake_token = "mocked.jwt.token"
        mock_generate_token.return_value = fake_token

        # Execute Request by simulating html form
        response = self.client.post("/login", data={
            "username": "X009",
            "password": "5195556338"
        })

        # assert
        # check if redirects
        self.assertEqual(response.status_code, 302)
        # check if redirected to home page
        self.assertEqual(response.location, "/")
        
        # Check Header and Cookie still get set on redirect
        self.assertEqual(response.headers.get("Authorization"), f"Bearer {fake_token}")
        
        cookies = response.headers.getlist('Set-Cookie')
        cookie_found = any(f'jwt_token={fake_token}' in cookie for cookie in cookies)
        self.assertTrue(cookie_found)
        
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