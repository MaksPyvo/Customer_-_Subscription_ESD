from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)

@app.route('/')
def home():
   return "Hello, Flask!"

@app.route('/login')
def login():
   return render_template('login.html')
 
if __name__ == '__main__':
   app.run(debug=True)