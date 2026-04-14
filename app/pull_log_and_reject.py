import os
import paramiko
from dotenv import load_dotenv

# Load env variables
load_dotenv()
SFTP_HOST = os.getenv("CFP_HOST")
SFTP_PORT = int(os.getenv("CFP_PORT", 22))
SFTP_USER = os.getenv("CFP_USER")
SFTP_PASS = os.getenv("CFP_PASS")

def download_debug_files():
    # 1. Create a local debug directory so we don't mix these up with primary data
    local_dir = "./data/cfp_data/debug"
    os.makedirs(local_dir, exist_ok=True)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to CFP SFTP server at {SFTP_HOST}...")
        # Connect to sftp server with env variables
        ssh.connect(hostname=SFTP_HOST, port=SFTP_PORT, username=SFTP_USER, password=SFTP_PASS)
        sftp = ssh.open_sftp()
        
        # --- 2. Download the status.json log file ---
        remote_log_path = "/cfp-log/status.json" #
        local_log_path = os.path.join(local_dir, "status.json")
        
        print(f"\nAttempting to download {remote_log_path}...")
        try:
            sftp.get(remote_log_path, local_log_path)
            print("✅ Successfully downloaded status.json")
        except Exception as e:
            print(f"❌ Could not download status.json: {e}")

        # --- 3. Download all files from the /reject directory ---
        remote_reject_dir = "/reject" #
        print(f"\nChecking {remote_reject_dir} for rejected files...")
        
        try:
            sftp.chdir(remote_reject_dir)
            reject_files = sftp.listdir()
            
            if not reject_files:
                print("✨ No files found in the /reject directory. You haven't made any bad uploads yet!")
            else:
                for filename in reject_files:
                    remote_file_path = f"{remote_reject_dir}/{filename}"
                    local_file_path = os.path.join(local_dir, filename)
                    
                    print(f"Downloading rejected file: {filename}...")
                    sftp.get(remote_file_path, local_file_path)
                print(f"✅ Downloaded {len(reject_files)} rejected file(s).")
                
        except Exception as e:
            print(f"❌ Could not access or download from /reject: {e}")
            
    except Exception as e:
        print(f"SFTP Connection Error: {e}")
    finally:
        # 1. Close the SFTP channel cleanly if it was created
        if 'sftp' in locals():
            sftp.close()
            
        # 2. Close the underlying SSH connection
        ssh.close()
        print(f"\n--- Disconnected. Check the '{local_dir}' folder to inspect the files! ---")

if __name__ == "__main__":
    download_debug_files()