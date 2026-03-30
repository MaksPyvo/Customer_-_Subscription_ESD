import os

# libraries
from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# modules
from app.modules.secret.secret import get_secret
from app.modules.database.database import db
from app.modules.CFP.primary import download_primary_files
from app.modules.CFP.schedule import scheduled_primary_sync
from app.modules.database.sync_primary import sync_primary_csv_to_db
from app.models.customer import Customer
# Load environment variables
load_dotenv()

app = Flask(__name__)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# config SQLAlchemy to db
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() or request.form
    client_id = data.get('username')
    mobile = data.get('password')

    customer = Customer.query.filter_by(client_id=client_id).first()

    if customer and customer.mobile == mobile:
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/customers')
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@app.route('/update-delivery', methods=['POST'])
def update_delivery():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid or missing JSON payload"}), 400
        
    client_id = data.get('client_id')
    if not client_id:
        return jsonify({"success": False, "message": "client_id is required"}), 400
    try:
       # get customer by client id
       customer = Customer.query.filter_by(client_id=client_id).first()

       if not customer:
         return jsonify({"success": False, "message": 'Customer not found'}), 404
        
       # update user counts
       customer.produce = customer.produce + int(data.get('produce', 0))
       customer.meat = customer.meat + int(data.get('meat', 0))
       customer.dairy = customer.dairy + int(data.get('dairy', 0))
       customer.delivery_count = customer.delivery_count + 1

       # save database
       db.session.commit()
       return jsonify({"success": True, "message": "Delivery counts updated successfully."}), 200

    except Exception as e:
       # discard changes if error occurs
       db.session.rollback() 
       return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

@app.route('/providers')
def providers():
   return render_template('providers.html')

@app.route('/info')
def info():
   return render_template('info.html')
 
@app.route('/secret', methods=['GET'])
def get_dt_secret():
   try:
      # get db secret
      data = get_secret()
      
      secret = data.get('secret')
      # print("customer and subscriptions secret: ", secret)
      # returns as json for now...
      return render_template('secrets.html', secret=secret)
        
   except Exception as e:
      # error handling
      return jsonify({"error": str(e)}), 500

   
   
if __name__ == '__main__':
   # download CFP CSV files on start up for now
   # need to update logic when it should be called

   
   with app.app_context():
      # download /primary CFP files
      download_primary_files()
      # set directory
      primary_dir = "app/data/cfp_data"
      
      # update db with primary files
      sync_primary_csv_to_db(primary_dir)
      
      # setup scheduler
      scheduler = BackgroundScheduler()
      
      # run scheduled_primary_sync function every 60s (change to an hour for deployment)
      scheduler.add_job(
            func=scheduled_primary_sync, 
            args=[app], 
            trigger="interval", 
            seconds=60
            #hours=1
      )
      
      scheduler.start()
      
   app.run(host='0.0.0.0', port=7500, debug=True)
