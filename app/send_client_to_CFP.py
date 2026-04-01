from modules.CFP.revision import upload_revision_file, parse_city
import os
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
local_path = os.path.join(script_dir, "../..", "data/cfp_data/")
from dotenv import load_dotenv

# Load env variables just like in primary.py
load_dotenv()
SFTP_HOST = os.getenv("CFP_HOST")
SFTP_PORT = int(os.getenv("CFP_PORT", 22)) # Ensure port is an integer
SFTP_USER = os.getenv("CFP_USER")
SFTP_PASS = os.getenv("CFP_PASS")

class DummyClient:
    def __init__(self):
        self.client_id = "H478"
        self.address = "123 Fake St, Kitchener, ON"
        self.mobile = "5195551234"
        self.delivery_count = 11
        self.produce = 5
        self.meat = 6
        self.dairy = 5

if __name__ == "__main__":
    dummy_client = DummyClient()
    city = parse_city(dummy_client)
    if city == "Unknown":
        print("Could not parse city from client address.")
    else:
        success = upload_revision_file(dummy_client, city)
        if success:
            print("Revision file uploaded successfully.")
        else:
            print("Failed to upload revision file.")