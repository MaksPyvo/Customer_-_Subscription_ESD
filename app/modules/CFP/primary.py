import os
import paramiko
from dotenv import load_dotenv

# load env variables
load_dotenv()
SFTP_HOST = os.getenv("CFP_HOST")
SFTP_PORT = os.getenv("CFP_PORT")
SFTP_USER = os.getenv("CFP_USER")
SFTP_PASS = os.getenv("CFP_PASS")

def download_primary_files():
    # create local directory to download csv files
    local_dir = "./app/data/cfp_data"
    # create directory
    os.makedirs(local_dir, exist_ok=True)
    
    # ssh into CFP
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to CFP SFTP server at {SFTP_HOST}...")
        # connect to sftp server with env variables
        ssh.connect(hostname=SFTP_HOST, port=SFTP_PORT, username=SFTP_USER, password=SFTP_PASS)
        
        # open sftp session on server after SSHing
        sftp = ssh.open_sftp()
      
        primary_dir = '/primary'
        
        # change directory to primary directory on server
        sftp.chdir(primary_dir)
        
        # list all files in the directory
        files = sftp.listdir()
        print(f"Files in {primary_dir}: {files}")
        
        downloaded_files = []
        
        # loop through and download the CSV files
        for filename in files:
            if filename.endswith('.csv'):
                remote_file_path = f"{primary_dir}/{filename}"
                local_file_path = os.path.join(local_dir, filename)
                
                print(f"Downloading {filename}...")
                
                # download file from remote path to local path
                sftp.get(remote_file_path, local_file_path)
                
                # add to array of files
                downloaded_files.append(local_file_path)
                
        print("Downloading /primary files complete")
        return downloaded_files
        
    except Exception as e:
        print(f"SFTP Error: {e}")
        return []
    finally:
        # close the connection
        ssh.close()

if __name__ == "__main__":
    download_primary_files()