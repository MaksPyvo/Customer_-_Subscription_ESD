from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    def __repr__(self):
        return f"Customer {self.client_id}"