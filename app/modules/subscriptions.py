import requests
from sqlalchemy import null, text, true, update
from sqlalchemy.orm import joinedload
import jwt

from app.models.customer import Customer
from app.modules.database.database import db
from flask import request

from app.models.subscription import Subscription
from datetime import datetime, timedelta, date
from app.app import app
from app.modules.auth.auth import generate_token
from app.config import Config

@app.route('/api/v1/subscriptions', methods=['POST'])
def add_subscription():
    # get data
    data = request.get_json()
    occurence = data.get('occurence', 'weekly')
    quantity = data.get('qty', 1)
    today = datetime.now().date()
    
    # calculate next order date
    next_date = calculate_next_order_date(occurence)

    try:
        # add to db
        new_sub = Subscription(
            product_id=data['product_id'],
            quantity=quantity,
            occurence=occurence,
            next_order=next_date
        )
        
        db.session.add(new_sub)
        db.session.commit()

        return {
            "status": "success",
            "data": None,
            "error": None
        }, 201

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": {"code": "DATABASE_ERROR", "message": str(e)}
        }, 400



def checkDailySubscriptions():
    
    # query database for subscriptions where next occurence == today
    # get customer id, product id, occurence and qty 
    result = db.session.query(Subscription).filter(Subscription.next_order == date.today()).all()
    
    for r in result:
        # update next order date
        place_order(r.customer_id, r.product_id, r.quantity)
        next_date = calculate_next_order_date(r.occurence)
        r.next_order = next_date
        db.session.commit()
        

def place_order(customer_id, product_id, qty):
    #Query the product using parameterized SQL
    query = text("SELECT name FROM products WHERE id = :pid")
    product_result = db.session.execute(query, {"pid": product_id}).fetchone()
    
    if not product_result:
        return {"error": "Product not found"}
        
    product_name = product_result[0]


    order_session = requests.Session()

    customer = db.session.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"error": "Customer not found"}

    JWT_token = generate_token(customer.client_id)
    #Initiate Checkoout
    initiate_checkout_json = {
        "items": [
            {
                "productId":   product_id,
                "productName": product_name,
                "quantity":    qty,
                "unit":        "kg"
            }
        ],
        "userToken": JWT_token, 
        "clientID": customer.client_id
    }
    
    try:
        # call checkout API
        init_response = order_session.post('http://165.22.230.110:5001/checkout/initiate', json=initiate_checkout_json)
        init_response.raise_for_status() # Raises an exception for 4xx/5xx status codes
        
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to initiate checkout", "details": str(e)}

    #Fetch Customer Address

    address_vector = parse_address(customer.address)
    
    #Submit Checkout
    submit_checkout_json = {
        "addressLine1": address_vector[0],
        "city":         address_vector[1],      
        "province":     address_vector[2],
        "postalCode":   address_vector[3],
        "dropOff":      True,  
    }

    try:
        submit_response = order_session.post('http://165.22.230.110:5001/checkout/submit', json=submit_checkout_json)
        submit_response.raise_for_status()
        
        #Return the successful response
        return {"status": "success", "data": submit_response.json()}
    #Handle any exceptions that occur during the API call    
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to submit checkout", "details": str(e)}


    

@app.route('/api/v1/subscriptions', methods=['DELETE'])
def deleteSubscription():
    data = request.get_json()

    id = data.get('subscription_id')

    try: 
        db.session.query(Subscription).filter_by(id=id).delete()
        db.session.commit()

        return {
            "status": "success",
            "data": None,
            "error": None
        }, 201

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": {"code": "DATABASE_ERROR", "message": str(e)}
        }, 400

def calculate_next_order_date(occurence):
    today = date.today()
    if occurence == 'weekly':
        next_date = today + timedelta(weeks=1)
    elif occurence == 'biweekly':
        next_date = today + timedelta(weeks=2)
    elif occurence == 'monthly':
        next_date = today + timedelta(days=30)
    elif occurence == '3months':
        next_date = today + timedelta(days=90)
    elif occurence == '6months':
        next_date = today + timedelta(days=180)
    elif occurence == 'yearly':
        next_date = today + timedelta(days=365)
    else:
        next_date = today + timedelta(days=7) 
    return next_date

# Helper function to parse address string into components
def parse_address(address_string):
    #Split the string by commas and clean up extra spaces
    parts = [part.strip() for part in address_string.split(',')]
    
    #Split the final chunk by the FIRST space only
    prov_and_postal = parts[2].split(maxsplit=1)
    
    #Assemble and return the final list
    return [parts[0], parts[1], prov_and_postal[0], prov_and_postal[1]]


@app.route('/api/v1/subscriptions', methods=['PATCH'])
def update_subscription():
    #get data from json
    data = request.get_json()
    sub_id = data.get('id')
    occurence = data.get('occurence')
    quantity = data.get('qty')
    
    if not sub_id:
        return {"status": "error", "error": {"message": "Subscription ID is required"}}, 400

    try:
        # fetch from db
        sub = db.session.query(Subscription).filter_by(id=sub_id).first()

        if not sub:
            return {"status": "error", "error": {"message": "Subscription not found"}}, 404

        # update
        if occurence:
            sub.occurence = occurence
            #recaclulate order date
            sub.next_order = calculate_next_order_date(occurence)
        
        if quantity is not None:
            sub.quantity = quantity

        db.session.commit()

        return {
            "status": "success",
            "data": sub.to_dict(),
            "error": None
        }, 200

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": {"code": "DATABASE_ERROR", "message": str(e)}
        }, 400

@app.route('/api/get_subscriptions', methods=['GET'])
def get_subscriptions():
    token = session.get("user_token")
    if not token:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        # get client id from token
        payload = jwt.decode(token, Config.CS_JWT_PASS, algorithms=["HS256"])
        token_client_id = payload["client_id"]

        #join tables to get product name and customer id from client id in token
        query = text("""
            SELECT 
                s.id, 
                s.occurence, 
                s.quantity, 
                s.next_order, 
                p.name AS product_name
            FROM subscriptions s
            JOIN products p ON s.product_id = p.id
            JOIN customers c ON s.customer_id = c.id
            WHERE c.client_id = :token_cid
        """)
        
        results = db.session.execute(query, {"token_cid": token_client_id}).mappings().all()
        
        # add to database
        subscriptions = []
        for row in results:
            subscriptions.append({
                "id": row['id'],
                "product_name": row['product_name'],
                "occurence": row['occurence'],
                "quantity": row['quantity'],
                "next_order": row['next_order'].isoformat() if row['next_order'] else None
            })

        return jsonify(subscriptions), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500