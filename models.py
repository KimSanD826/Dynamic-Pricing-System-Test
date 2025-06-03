from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.String(50), primary_key=True)
    base_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)  # Added cost_price
    inventory = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    sales_last_30_days = db.Column(db.Integer)
    average_rating = db.Column(db.Float)
    category = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'base_price': self.base_price,
            'cost_price': self.cost_price,
            'inventory': self.inventory,
            'current_price': self.current_price,
            'sales_last_30_days': self.sales_last_30_days,
            'average_rating': self.average_rating,
            'category': self.category
        }
class HistoricalSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'))
    date = db.Column(db.Date, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
