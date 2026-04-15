import os
import csv
import paramiko
from dotenv import load_dotenv

# Load env variables just like in primary.py
load_dotenv()
SFTP_HOST = os.getenv("CFP_HOST")
SFTP_PORT = int(os.getenv("CFP_PORT", 22)) # Ensure port is an integer
SFTP_USER = os.getenv("CFP_USER")
SFTP_PASS = os.getenv("CFP_PASS")

def upload_revision_file(client, city):
    # Generate filename based on city
    filename=f"rev-CFP-{city}.csv"
    local_path = f"./app/data/cfp_data/"
    local_file_path = os.path.join(local_path, filename)

    # Construct remote file path
    remote_file_path = f"/incoming/{filename}"

    try:
        with open(local_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header required by the CFP schema
            writer.writerow(['clientID', 'address', 'mobile', 'deliveryCount', 'produce', 'meat', 'dairy'])
            
            # Write the updated customer data
            writer.writerow([
                client.client_id,
                client.address,
                client.mobile,
                client.delivery_count,
                client.produce,
                client.meat,
                client.dairy
            ])
    except Exception as e:
        print(f"Error creating local CSV file: {e}")
        return False
    
    # Upload the file to the CFP SFTP server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=SFTP_HOST, port=SFTP_PORT, username=SFTP_USER, password=SFTP_PASS)
        sftp = ssh.open_sftp()
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        print(f"Error uploading file to SFTP server: {e}")
        return False
    
def parse_city(client):
    # Simple parsing logic based on address content
    if "Kitchener" in client.address:
        return "Kitchener"
    elif "Waterloo" in client.address:
        return "Waterloo"
    elif "Cambridge" in client.address:
        return "Cambridge"
    else:
        return "Unknown"
