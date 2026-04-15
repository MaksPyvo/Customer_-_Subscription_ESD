from flask_sqlalchemy import SQLAlchemy
from app.modules.database.database import db

class Subscription(db.Model):
    __tablename__ = 'subscription'

    # primary key
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity= db.Column(db.Integer, nullable=False,default=1)
    occurence = db.Column(db.String, nullable=False)
    next_order = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "occurence": self.occurence,
            "next_order": self.next_order.isoformat() if self.next_order else None,
            "quantity": self.quantity
        }