import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app

# generate JWT token
def generate_token(client_id):
    # Set expiration time for 4hrs
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4)
    
    # current_app to get access to the secret key without importing the app object directly
    token = jwt.encode(
        {
            'client_id': client_id, 
            'exp': expiration
        }, 
        current_app.config['secret_key'], 
        algorithm="HS256"
    )
    return token

# get token from user session after logging in
def get_token_from_request():
    token = None
    
    # check for the token in the headers first
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]

    # check for token in cookies second
    if not token:
        token = request.cookies.get('jwt_token')

    # try query string third
    if not token:
        token = request.args.get('token')
        
    return token

# get client_id from jwt token
def get_client_id_from_jwt():
    # get token string
    token = get_token_from_request()
    
    if not token:
        return None
        
    try:
        # decode token
        data = jwt.decode(token, current_app.config['secret_key'], algorithms=["HS256"])
        
        # return the client_id from jwt
        return data.get('client_id')
        
    except jwt.ExpiredSignatureError:
        # Token exists but has expired
        return None
    except jwt.InvalidTokenError:
        # Token exists but is fake/tampered with
        return None

# helper function for reading token for routes
# need to pass current_client_id from route
def token_required(f): # f = route
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Decode the token
            data = jwt.decode(token, current_app.config['secret_key'], algorithms=["HS256"])
            
            # Extract the client_id that we put into the token during login
            current_client_id = data['client_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
            
        # Pass the current_client_id as the first argument to the route function
        return f(current_client_id, *args, **kwargs)
        
    return decorated