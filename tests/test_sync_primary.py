import unittest
from unittest.mock import patch, mock_open
from app.modules.database.sync_primary import sync_primary_csv_to_db


class TestSyncPrimary(unittest.TestCase):
    @patch("app.modules.database.sync_primary.db")
    @patch("app.modules.database.sync_primary.glob.glob")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "clientID,address,mobile,produce,meat,dairy,deliveryCount\n"
            "I985,332 Westmount Rd.,5195558691,1,0,0,2\n"
        )
    )
    def test_sync_primary_csv_to_db(self, mock_file, mock_glob, mock_db):
        mock_glob.return_value = ["fake.csv"]

        sync_primary_csv_to_db("some/path")

        self.assertTrue(mock_db.session.execute.called)
        self.assertTrue(mock_db.session.commit.called)

    @patch("app.modules.database.sync_primary.db")
    def test_sync_primary_no_path(self, mock_db):
        sync_primary_csv_to_db(None)
        self.assertFalse(mock_db.session.execute.called)
        self.assertFalse(mock_db.session.commit.called)


if __name__ == "__main__":
    unittest.main()