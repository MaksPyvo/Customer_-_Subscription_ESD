from app.modules.database.database import db
from sqlalchemy.dialects.postgresql import insert, delete, request, session
from app.models.subscription import Subscription
from datetime import datetime, timedelta, today
from app.app import app

@app.route('/api/v1/subscriptions', methods=['POST'])
def add_subscription():
    # get data
    data = request.get_json()
    occurence = data.get('occurence', 'weekly')
    quantity = data.get('qty', )
    today = datetime.now().date()
    
    # calculate next order date
    next_date = calculate_next_order_date(occurence)

    try:
        # add to db
        new_sub = Subscription(
            product_id=data['product_id'],
            qty=quantity,
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
    result = session.query(Subscription).with_entities(Subscription.customer_id, Subscription.product_id, Subscription.qty, Subscription.occurence).filter(Subscription.next_order = date.today()).all()
    
    for r in result:
        # update next order date
        next_date = calculate_next_order_date(r.occurence)

        # place order

    

@app.route('/api/v1/subscriptions', methods=['DELETE'])
def deleteSubscription():
    data = request.get_json()

    id = data.get('subscription_id')

    try: 
        query = Subscription.delete().where(Subscription.c.subscription_id == id)
        db.session.add(query)
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

    if occurence == 'weekly':
        next_date = today + timedelta(weeks=1)
    elif occurence == 'bi-weekly':
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