import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from app.modules.CFP.revision import upload_revision_file 

# Create a dummy client
class DummyClient:
    def __init__(self):
        self.client_id = "K123"
        self.address = "123 Fake St, Kitchener, ON"
        self.mobile = "5195551234"
        self.delivery_count = 5
        self.produce = 2
        self.meat = 1
        self.dairy = 1

class TestRevisionUpload(unittest.TestCase):

    def setUp(self):
        self.dummy_client = DummyClient()
        self.city = "Kitchener"

    # Happy path
    #create mocks for both file writing and SFTP upload
    @patch('app.modules.CFP.revision.paramiko.SSHClient')
    @patch('builtins.open', new_callable=mock_open)
    def test_upload_revision_file_success(self, mock_file, mock_ssh_class):
        # Setup our mocked SSH/SFTP connection
        mock_ssh_instance = MagicMock()
        mock_ssh_class.return_value = mock_ssh_instance
        mock_sftp_instance = MagicMock()
        mock_ssh_instance.open_sftp.return_value = mock_sftp_instance

        result = upload_revision_file(self.dummy_client, self.city)

        self.assertTrue(result)
        
        mock_file.assert_called_once_with(
            './app/data/cfp_data/rev-CFP-Kitchener.csv', 
            mode='w', newline='', encoding='utf-8'
        )
        
        mock_sftp_instance.put.assert_called_once_with(
            './app/data/cfp_data/rev-CFP-Kitchener.csv', 
            '/incoming/rev-CFP-Kitchener.csv'
        )

    # File writing fails (e.g., permission error)
    
    @patch('builtins.open', side_effect=PermissionError("Cannot write file"))
    def test_upload_revision_file_csv_error(self, mock_file):

        result = upload_revision_file(self.dummy_client, self.city)

        self.assertFalse(result)

    # SFTP upload fails (e.g., connection error)
    @patch('app.modules.CFP.revision.paramiko.SSHClient')
    def test_upload_revision_file_sftp_error(self, mock_ssh_class):
        
        mock_ssh_instance = MagicMock()
        mock_ssh_class.return_value = mock_ssh_instance
        mock_ssh_instance.connect.side_effect = Exception("SFTP Timeout")
        
        result = upload_revision_file(self.dummy_client, self.city)

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()