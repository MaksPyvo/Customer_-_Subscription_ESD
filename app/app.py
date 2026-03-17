from flask import Flask, render_template, request, jsonify, make_response

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
 
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=7500, debug=True)