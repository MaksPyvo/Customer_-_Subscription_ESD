import unittest
from unittest.mock import patch, MagicMock
from app.modules.secret.secret import get_secret


class TestSecret(unittest.TestCase):
    @patch("app.modules.secret.secret.get_db_connection")
    def test_get_secret_returns_record(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = {
            "id": 5,
            "secret": "uiTeam",
            "teamname": "Customer and Subscriptions"
        }

        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        result = get_secret()

        self.assertEqual(result["id"], 5)
        self.assertEqual(result["secret"], "uiTeam")
        self.assertEqual(result["teamname"], "Customer and Subscriptions")

        mock_cursor.execute.assert_called_once_with("SELECT * FROM dtsecrets where id = 5;")
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()