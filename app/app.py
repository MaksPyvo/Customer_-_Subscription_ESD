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
      return render_template('secrets.html', secret=secret)
        
   except Exception as e:
      # error handling
      return jsonify({"error": str(e)}), 500

   
   
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=7500, debug=True)