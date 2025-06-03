from flask import Flask, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from config import Config
from models import db, Product, HistoricalSale
from pricing_logic import predict_optimal_price, apply_business_rules, get_competitor_prices, initialize_model


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)
db.init_app(app)

# Initialize the API
api = Api(app, version='1.0', title='Dynamic Pricing System API')
ns = api.namespace('api', description='Pricing operations')

# Initialize the model when the app starts
with app.app_context():
    db.create_all()  # Create tables
    initialize_model()  # Initialize and train the model

# Request/Response models
product_model = api.model('Product', {
    'product_id': fields.String(required=True),
    'base_price': fields.Float,
    'cost_price': fields.Float,
    'inventory': fields.Integer,
    'current_price': fields.Float,
    'sales_last_30_days': fields.Integer,
    'average_rating': fields.Float,
    'category': fields.String
})

@ns.route('/products')
class ProductList(Resource):
    @ns.marshal_list_with(product_model)
    def get(self):
        """Get all products"""
        return Product.query.all()

@ns.route('/products/<string:product_id>')
class ProductResource(Resource):
    @ns.marshal_with(product_model)
    def get(self, product_id):
        """Get single product"""
        product = Product.query.get_or_404(product_id)
        return product

@ns.route('/pricing/update')
class PricingUpdate(Resource):
    
    def post(self):
        products = Product.query.all()
        competitor_prices = get_competitor_prices()
        updated_products = []

        for product in products:
            # Fetch historical data
            historical_data = HistoricalSale.query.filter_by(
                product_id=product.product_id
            ).all()
            
            ml_price = predict_optimal_price(
                product.to_dict(),
                historical_data
            )
            # Apply business rules
            comp_price = competitor_prices.get(product.product_id)
            new_price = apply_business_rules(
                ml_price,
                product.to_dict(),
                comp_price
            )
            
            # Update product
            product.current_price = new_price
            updated_products.append({
                'product_id': product.product_id,
                'new_price': new_price
            })
        
        db.session.commit()
        return jsonify({
            'message': f'Updated {len(updated_products)} products',
            'updates': updated_products
        })

@ns.route('/dashboard')
class DashboardData(Resource):
    def get(self):
        """Get all data needed for the dashboard"""
        try:
            products = Product.query.all()
            if not products:
                return {"error": "No products found"}, 404
                
            competitor_prices = get_competitor_prices()
            print(f"Found {len(products)} products and {len(competitor_prices)} competitor prices")
            
            dashboard_data = []
            for product in products:
                try:
                    # Get historical sales data
                    historical_data = HistoricalSale.query.filter_by(
                        product_id=product.product_id
                    ).all()
                    print(f"Found {len(historical_data)} historical records for product {product.product_id}")
                    
                    # Prepare product data
                    product_dict = {
                        'product_id': product.product_id,
                        'base_price': float(product.base_price),
                        'cost_price': float(product.cost_price),
                        'current_price': float(product.current_price),
                        'inventory': int(product.inventory),
                        'sales_last_30_days': int(product.sales_last_30_days),
                        'average_rating': float(product.average_rating),
                        'competitor_price': float(competitor_prices.get(product.product_id, product.current_price))
                    }
                    
                    # Calculate adjusted price
                    ml_price = predict_optimal_price(product_dict, historical_data)
                    adjusted_price = apply_business_rules(
                        ml_price,
                        product_dict,
                        product_dict['competitor_price']
                    )
                    
                    dashboard_data.append({
                        'id': product.product_id,
                        'name': f"Product {product.product_id}",
                        'current_price': float(product.current_price),
                        'adjusted_price': float(adjusted_price),
                        'inventory': int(product.inventory),
                        'sales': int(product.sales_last_30_days),
                        'competitor_price': float(competitor_prices.get(product.product_id, 0))
                    })
                    print(f"Processed product {product.product_id}")
                    
                except Exception as e:
                    print(f"Error processing product {product.product_id}: {str(e)}")
                    continue
            
            if not dashboard_data:
                return {"error": "No data could be processed"}, 500
                
            print(f"Returning {len(dashboard_data)} products")
            return dashboard_data
            
        except Exception as e:
            print(f"Dashboard error: {str(e)}")
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)