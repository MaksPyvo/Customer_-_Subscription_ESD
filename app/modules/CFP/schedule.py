from app.modules.CFP.primary import download_primary_files
from app.modules.database.sync_primary import sync_primary_csv_to_db

# background job to sync CFP primary data
# need to pass Flask app object for db context
def scheduled_primary_sync(app):
    print("\nStarting Scheduled /primary CFP Sync")
    
    with app.app_context():
        try:
            download_primary_files()
            primary_dir = "app/data/cfp_data"
            sync_primary_csv_to_db(primary_dir)
            print("--- Scheduled CFP Sync Complete ---\n")
        except Exception as e:
            print(f"--- Scheduled Sync Failed: {e} ---\n")