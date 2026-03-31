import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

# Adjust this import to match wherever you saved your revision function
from app.modules.CFP.revision import upload_revision_file 

# 1. Create a dummy client
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

        # Call your function
        result = upload_revision_file(self.dummy_client, self.city)

        # Assertions to verify the code did what we expected
        self.assertTrue(result)
        
        # Verify it tried to create the correct file
        mock_file.assert_called_once_with(
            './app/data/cfp_data/rev-CFP-Kitchener.csv', 
            mode='w', newline='', encoding='utf-8'
        )
        
        # Verify SFTP connect and put were called with correct remote path
        mock_sftp_instance.put.assert_called_once_with(
            './app/data/cfp_data/rev-CFP-Kitchener.csv', 
            '/incoming/rev-CFP-Kitchener.csv'
        )

    # File writing fails (e.g., permission error)
    
    @patch('builtins.open', side_effect=PermissionError("Cannot write file"))
    def test_upload_revision_file_csv_error(self, mock_file):
        # Call your function, which should hit the first 'except' block
        result = upload_revision_file(self.dummy_client, self.city)

        # It should return False because it couldn't write the file
        self.assertFalse(result)

    # SFTP upload fails (e.g., connection error)
    @patch('app.modules.CFP.revision.paramiko.SSHClient')
    def test_upload_revision_file_sftp_error(self, mock_ssh_class):
        # Setup SSH mock to throw an error when connecting
        mock_ssh_instance = MagicMock()
        mock_ssh_class.return_value = mock_ssh_instance
        mock_ssh_instance.connect.side_effect = Exception("SFTP Timeout")

        # Call your function, which should hit the second 'except' block
        result = upload_revision_file(self.dummy_client, self.city)

        # It should return False because the upload failed
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()