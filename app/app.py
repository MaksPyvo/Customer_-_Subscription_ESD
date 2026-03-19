from flask import Flask, render_template, request, jsonify, make_response
from modules.secret.secret import get_secret

app = Flask(__name__)

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
      #return render_template('secrets.html', secret=secret)
      return jsonify({"secret": secret}) 
   except Exception as e:
      # error handling
      return jsonify({"error": str(e)}), 500

from flask import request, render_template, jsonify
import requests

@app.route('/secrets', methods=['GET'])
def get_dt_secrets():
    try:
        # 1. Get this module's secret (Customer & Subscriptions)
        data = get_secret()
        secret = data.get('secret')

        # 2. Extract ports from query parameters
        port1 = request.args.get('port1')
        port2 = request.args.get('port2')
        port3 = request.args.get('port3')
        port4 = request.args.get('port4')

        base_ip = "http://165.22.230.110"

        # 3. Helper function to fetch secrets from other modules
        def fetch_secret_from_service(port):
            if not port:
                return "Port not provided in URL"
            try:
                # Add a timeout so a hanging service doesn't freeze your route
                response = requests.get(f"{base_ip}:{port}/secret", timeout=5)
                response.raise_for_status() # Raise exception for 4xx/5xx errors
                
                # Parse the expected {"secret": "value"} JSON format
                return response.json().get('secret', 'Key "secret" missing')
            except requests.RequestException as req_e:
                return f"Request failed: {str(req_e)}"

        # 4. Fetch the secrets for the remaining 4 modules
        # Mapping based on your HTML table order
        secret2 = fetch_secret_from_service(port1) # Delivery Execution
        secret3 = fetch_secret_from_service(port2) # Order Orchestration
        secret4 = fetch_secret_from_service(port3) # Product & Inventory Intelligence
        secret5 = fetch_secret_from_service(port4) # Supply & Network Management

        # 5. Pass all variables to the Jinja template
        return render_template(
            'secrets.html', 
            secret=secret,
            secret2=secret2,
            secret3=secret3,
            secret4=secret4,
            secret5=secret5
        )
        
    except Exception as e:
        # Global error handling
        return jsonify({"error": str(e)}), 500
   
   
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=7500, debug=True)