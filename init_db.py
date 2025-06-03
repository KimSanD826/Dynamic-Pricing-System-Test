from app import app, db
from models import Product, HistoricalSale
from datetime import datetime

sample_data = [
    {
        "product_id": "P001",
        "base_price": 100.0,
        "cost_price": 70.0,
        "inventory": 15,
        "current_price": 100.0,
        "sales_last_30_days": 120,
        "average_rating": 4.5,
        "category": "Electronics"
    },
    {
        "product_id": "P002",
        "base_price": 200.0,
        "cost_price": 140.0,
        "inventory": 50,
        "current_price": 200.0,
        "sales_last_30_days": 40,
        "average_rating": 4.0,
        "category": "Apparel"
    },{
        "product_id": "P003",
        "base_price": 50.0,
        "cost_price": 35.0,
        "inventory": 5,
        "current_price": 50.0,
        "sales_last_30_days": 10,
        "average_rating": 3.8,
        "category": "Home"
    }
]

historical_sales = [
    {"product_id": "P001", "date": "2024-10-01", "units_sold": 5, "price": 95.0},
    {"product_id": "P001", "date": "2024-10-02", "units_sold": 10, "price": 90.0},
    {"product_id": "P002", "date": "2024-10-01", "units_sold": 3, "price": 190.0},
    {"product_id": "P003", "date": "2024-10-01", "units_sold": 1, "price": 48.0}
]

def parse_date(date_str):
    """Convert string date to datetime object"""
    return datetime.strptime(date_str, '%Y-%m-%d')
def initialize_database():
    with app.app_context():
        db.create_all()
        for data in sample_data:
            if not Product.query.get(data['product_id']):
                product = Product(**data)
                
                db.session.add(product)    
        
        for sale in historical_sales:
            # Convert date string to Python date object
            sale['date'] = parse_date(sale['date'])
            
            # Create new historical record
            db.session.add(HistoricalSale(**sale))
        
        # Commit all changes
        db.session.commit()
        print("Database initialized with sample products and historical sales!")

if __name__ == '__main__':
    initialize_database()