from flask_sqlalchemy import SQLAlchemy
from app.modules.database.database import db

class Customer(db.Model):
    __tablename__ = 'customer'

    # primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # CFP client_id
    client_id = db.Column(db.String(5), unique=True, nullable=False)
    
    address = db.Column(db.String(255))
    mobile = db.Column(db.String(15))
    produce = db.Column(db.Integer)
    meat = db.Column(db.Integer)
    dairy = db.Column(db.Integer)
    delivery_count = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "address": self.address,
            "mobile": self.mobile,
            "produce": self.produce,
            "meat": self.meat,
            "dairy": self.dairy,
            "delivery_count": self.delivery_count
        }