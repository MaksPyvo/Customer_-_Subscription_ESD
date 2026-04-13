import os

# libraries
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import jwt
import datetime

# modules
from app.modules.secret.secret import get_secret
from app.modules.database.database import db
from app.modules.CFP.primary import download_primary_files
from app.modules.CFP.schedule import scheduled_primary_sync
from app.modules.database.sync_primary import sync_primary_csv_to_db
from app.models.customer import Customer
from app.modules.CFP.revision import upload_revision_file
from app.modules.CFP.revision import parse_city
from app.modules.auth.auth import generate_token, token_required, get_client_id_from_jwt, get_token_from_request

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
# get secretkey from env
app.config['secret_key'] = os.getenv("JWT_PASS")

db.init_app(app)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
   # load html page if GET request
   if request.method == 'GET':
      return render_template('login.html')

   # check if request is a json POST req
   is_json_request = request.is_json
   
   if is_json_request:
      # get data from json body
      data = request.get_json()
      client_id = data.get('username')
      mobile = data.get('password')
   else:
      # get data from form data
      client_id = request.form.get('username')
      mobile = request.form.get('password')

   # query the db for user
   customer = Customer.query.filter_by(client_id=client_id).first()
   
   # if id and mobile match then login
   if customer and customer.mobile == mobile:
      token = generate_token(customer.client_id)
      
      # if json request return 200 and token
      if is_json_request:
         response = jsonify({
               "message": "Login successful", 
               "token": token 
         }), 200

      # if form request redirect to home
      else:
         response = redirect(url_for('home')) 

      # set cookie and header with token
      response.set_cookie('jwt_token', token, httponly=True, secure=False)
      response.headers['Authorization'] = f'Bearer {token}'
      
      return response 
      
   # If login fails, re-render the login page and pass an error message
   else:
      if is_json_request:
         # return json back if through json
         return jsonify({"error": "Invalid credentials"}), 401
      else:
         # re-render login
         return render_template('login.html', error="Invalid credentials"), 401
      
@app.route('/logout')
def logout():
   # redirect to home page
   response = redirect(url_for('home'))
   
   # delete the JWT cookie
   response.delete_cookie('jwt_token')

   return response

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

       # upload revision file to CFP SFTP server
       customer_city = parse_city(customer)
       if customer_city == "Unknown":
          raise Exception("Could not parse city from customer address")
       if upload_revision_file(customer, customer_city)==False:
          raise Exception("Failed to upload revision file to SFTP server")
       
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

      return render_template('secrets.html', secret=secret)
        
   except Exception as e:
      # error handling
      return jsonify({"error": str(e)}), 500

@app.route('/gettoken', methods=['GET'])
# @token_required
def get_token(): # need to pass current_client_id variable for token_required function
   client_id = get_client_id_from_jwt()
   token = get_token_from_request()
   
   if not token:
      response = "Not logged in"
      return jsonify({"success": False, "response": response}), 401
   
   return jsonify({"success": True, "jwt": token, "client_id": client_id}), 200

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
            # seconds=60
            hours=1
      )
      
      scheduler.start()
      
   app.run(host='0.0.0.0', port=7500, debug=True)
