from app import app, db
from models import Product, HistoricalSale

def test_database():
    with app.app_context():
        try:
            # Test Products
            products = Product.query.all()
            print(f"Number of products: {len(products)}")
            if products:
                print("\nSample product:")
                print(products[0].to_dict())
            
            # Test Historical Sales
            sales = HistoricalSale.query.all()
            print(f"\nNumber of historical sales: {len(sales)}")
            if sales:
                print("\nSample sale:")
                print({
                    'id': sales[0].id,
                    'product_id': sales[0].product_id,
                    'date': str(sales[0].date),
                    'units_sold': sales[0].units_sold,
                    'price': sales[0].price
                })
            
        except Exception as e:
            print(f"Database error: {str(e)}")

if __name__ == "__main__":
    test_database() 