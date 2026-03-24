import os

# libraries
from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv

# modules
from modules.secret.secret import get_secret
from modules.database.database import db
from modules.CFP.primary import download_primary_files
from modules.database.sync_primary import sync_primary_csv_to_db

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

@app.route('/login')
def login():
   return render_template('login.html')

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
   download_primary_files()
   primary_dir = "app/data/cfp_data"
   
   with app.app_context():
      sync_primary_csv_to_db(primary_dir)
      
   app.run(host='0.0.0.0', port=7500, debug=True)