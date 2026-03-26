import os
import csv
import glob
from sqlalchemy.dialects.postgresql import insert
from app.modules.database.database import db
from app.models.customer import Customer

# """Reads CSVs and UPSERTs data into the database using SQLAlchemy."""
def sync_primary_csv_to_db(dir_path):
    if not dir_path:
        print("No files to process.")
        return

    search_csv = os.path.join(dir_path, "*.csv")
    csv_files = glob.glob(search_csv)
    
    total_synced = 0

    try:
        # read each CSV file
        for file in csv_files:
            print(f"Processing {file}...")
            
            # open and read csv file
            with open(file, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                for row in csv_reader:
                    # insert row into db
                    query = insert(Customer).values(
                        client_id=row['clientID'],
                        address=row['address'],
                        mobile=row['mobile'],
                        produce=int(row['produce']),
                        meat=int(row['meat']),
                        dairy=int(row['dairy']),
                        delivery_count=int(row['deliveryCount'])
                    )
                    
                    # if conflict (row already exists) update the row instead
                    upsert_query = query.on_conflict_do_update(
                        # check if client_id already exists in db and is never updated
                        index_elements=['client_id'],
                        # updates remaining columns to db
                        set_=dict(
                            address=query.excluded.address,
                            mobile=query.excluded.mobile,
                            produce=query.excluded.produce,
                            meat=query.excluded.meat,
                            dairy=query.excluded.dairy,
                            delivery_count=query.excluded.delivery_count
                        )
                    )
                    
                    # execute the statement
                    db.session.execute(upsert_query)
                    total_synced += 1
        
        # commit updates
        db.session.commit()
        print(f"Successfully updated {total_synced} customer records with primary data")

    except Exception as e:
        # rollback db if error
        db.session.rollback()
        print(f"Database Sync Error: {e}")