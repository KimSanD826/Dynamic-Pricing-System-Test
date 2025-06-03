import requests
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime

class DynamicPricingModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_importance = None
        
    def prepare_features(self, historical_data, product_data):
        """Prepare features for the model"""
        df = pd.DataFrame([{
            'date': h.date,
            'units_sold': h.units_sold,
            'price': h.price
        } for h in historical_data])
        
        if df.empty:
            return None, None
            
        # Time-based features
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Price-based features
        df['price_change'] = df['price'].pct_change().fillna(0)
        df['price_volatility'] = df['price'].rolling(window=7).std().fillna(0)
        
        # Sales-based features
        df['sales_ma7'] = df['units_sold'].rolling(window=7).mean().fillna(0)
        df['sales_ma30'] = df['units_sold'].rolling(window=30).mean().fillna(0)
        df['sales_trend'] = df['units_sold'].rolling(window=7).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        ).fillna(0)
        
        # Product features
        df['inventory_level'] = product_data['inventory']
        df['inventory_ratio'] = product_data['inventory'] / df['sales_ma30'].mean() if df['sales_ma30'].mean() > 0 else 1
        df['rating_factor'] = 1 + (product_data['average_rating'] - 3.5) * 0.1
        
        # Competitor features
        df['competitor_price'] = product_data.get('competitor_price', 0)
        df['price_difference'] = df['price'] - df['competitor_price']
        df['price_ratio'] = df['price'] / df['competitor_price'] if df['competitor_price'].mean() > 0 else 1
        
        # Select features for training
        feature_columns = [
            'day_of_week', 'month', 'is_weekend',
            'price_change', 'price_volatility',
            'sales_ma7', 'sales_ma30', 'sales_trend',
            'inventory_level', 'inventory_ratio',
            'rating_factor', 'price_difference', 'price_ratio'
        ]
        
        X = df[feature_columns].fillna(0)
        y = df['units_sold']
        
        return X, y
    
    def train(self, historical_data, product_data):
        """Train the model with historical data"""
        X, y = self.prepare_features(historical_data, product_data)
        if X is None or len(X) < 10:  # Need minimum data for training
            return False
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Store feature importance
        self.feature_importance = dict(zip(X.columns, self.model.feature_importances_))
        return True
    
    def predict_optimal_price(self, product_data, historical_data):
        """Predict optimal price using the trained model"""
        try:
            # Convert historical data to DataFrame for analysis
            hist_df = pd.DataFrame([{
                'date': h.date,
                'units_sold': h.units_sold,
                'price': h.price
            } for h in historical_data])
            
            if not hist_df.empty:
                # Calculate time-based features from historical data
                hist_df['date'] = pd.to_datetime(hist_df['date'])
                hist_df['day_of_week'] = hist_df['date'].dt.dayofweek
                hist_df['month'] = hist_df['date'].dt.month
                hist_df['is_weekend'] = hist_df['day_of_week'].isin([5, 6]).astype(int)
                
                # Get most common values for time features
                day_of_week = hist_df['day_of_week'].mode().iloc[0] if not hist_df['day_of_week'].empty else datetime.now().weekday()
                month = hist_df['month'].mode().iloc[0] if not hist_df['month'].empty else datetime.now().month
                is_weekend = hist_df['is_weekend'].mode().iloc[0] if not hist_df['is_weekend'].empty else int(datetime.now().weekday() in [5, 6])
                
                # Calculate price volatility from historical data
                price_volatility = hist_df['price'].std() if len(hist_df) > 1 else 0.1
                
                # Calculate sales trends
                sales_ma7 = hist_df['units_sold'].rolling(window=7).mean().iloc[-1] if len(hist_df) >= 7 else product_data['sales_last_30_days'] / 4
                sales_ma30 = hist_df['units_sold'].rolling(window=30).mean().iloc[-1] if len(hist_df) >= 30 else product_data['sales_last_30_days']
                sales_trend = hist_df['units_sold'].rolling(window=7).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
                ).iloc[-1] if len(hist_df) >= 7 else 0
            else:
                # Fallback to current date if no historical data
                current_date = datetime.now()
                day_of_week = current_date.weekday()
                month = current_date.month
                is_weekend = int(current_date.weekday() in [5, 6])
                price_volatility = 0.1
                sales_ma7 = product_data['sales_last_30_days'] / 4
                sales_ma30 = product_data['sales_last_30_days']
                sales_trend = 0
            
            # Get competitor price from API
            competitor_price = get_competitor_prices().get(product_data['product_id'])
            if competitor_price is None:
                competitor_price = product_data['current_price'] * 0.9  # Assume 10% lower than current price
            
            print(f"Using competitor price: {competitor_price} for product {product_data['product_id']}")
            
            # Calculate price range based on competitor price
            min_price = min(
                product_data['cost_price'] * 1.1,  # Minimum 10% above cost
                competitor_price * 0.8  # Or 20% below competitor
            )
            max_price = max(
                product_data['base_price'] * 1.5,  # Maximum 50% above base
                competitor_price * 1.2  # Or 20% above competitor
            )
            
            # Generate more price points for better granularity
            price_points = np.linspace(min_price, max_price, 100)
            
            best_price = product_data['current_price']
            best_revenue = 0
            
            # Prepare base features
            base_features = {
                'day_of_week': day_of_week,
                'month': month,
                'is_weekend': is_weekend,
                'price_change': 0.05,
                'price_volatility': price_volatility,
                'sales_ma7': sales_ma7,
                'sales_ma30': sales_ma30,
                'sales_trend': sales_trend,
                'inventory_level': product_data['inventory'],
                'inventory_ratio': product_data['inventory'] / max(product_data['sales_last_30_days'], 1),
                'rating_factor': 1 + (product_data.get('average_rating', 3.5) - 3.5) * 0.1,
                'competitor_price': competitor_price
            }
            
            # Try each price point
            for price in price_points:
                # Update price-dependent features
                current_features = base_features.copy()
                current_features['price_difference'] = price - competitor_price
                current_features['price_ratio'] = price / competitor_price if competitor_price > 0 else 1
                
                # Convert to DataFrame
                current_features_df = pd.DataFrame([current_features])
                
                # Scale features
                current_features_scaled = self.scaler.transform(current_features_df)
                
                # Predict sales
                predicted_sales = self.model.predict(current_features_scaled)[0]
                
                # Calculate revenue
                revenue = price * predicted_sales
                
                # Update best price if this one is better
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_price = price
            
            print(f"Best price found: {best_price} with revenue: {best_revenue}")
            return float(best_price)
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return predict_optimal_price_simple(product_data)

def predict_optimal_price_simple(product):
    """Fallback prediction method when ML model can't be used"""
    base_price = product.get('base_price', 0)
    inventory_factor = 1.2 if product.get('inventory', 0) < 10 else 0.9
    rating_factor = 1 + (product.get('average_rating', 3.5) - 3.5) * 0.1
    return base_price * inventory_factor * rating_factor


pricing_model = DynamicPricingModel()

def initialize_model():
    """Initialize and train the model with all historical data"""
    try:
        from models import Product, HistoricalSale
        from flask import current_app
        
        with current_app.app_context():
            # Get all products
            products = Product.query.all()
            print(f"Initializing model with {len(products)} products")
            
            # Get all historical data
            all_historical_data = HistoricalSale.query.all()
            print(f"Found {len(all_historical_data)} historical records")
            
            # Group historical data by product
            historical_by_product = {}
            for sale in all_historical_data:
                if sale.product_id not in historical_by_product:
                    historical_by_product[sale.product_id] = []
                historical_by_product[sale.product_id].append(sale)
            
            # Train model for each product
            for product in products:
                product_dict = {
                    'product_id': product.product_id,
                    'base_price': float(product.base_price),
                    'cost_price': float(product.cost_price),
                    'current_price': float(product.current_price),
                    'inventory': int(product.inventory),
                    'sales_last_30_days': int(product.sales_last_30_days),
                    'average_rating': float(product.average_rating)
                }
                
                historical_data = historical_by_product.get(product.product_id, [])
                if historical_data:
                    print(f"Training model for product {product.product_id} with {len(historical_data)} records")
                    pricing_model.train(historical_data, product_dict)
            
            print("Model initialization complete")
            
    except Exception as e:
        print(f"Error initializing model: {str(e)}")

def predict_optimal_price(product, historical_data):
    """Main function to predict optimal price"""
    try:
        # Try to use the ML model
        if pricing_model.train(historical_data, product):
            return pricing_model.predict_optimal_price(product, historical_data)
        # Fallback to simple prediction if ML model fails
        return predict_optimal_price_simple(product)
    except Exception as e:
        print(f"Error in predict_optimal_price: {str(e)}")
        return predict_optimal_price_simple(product)

def get_competitor_prices():
    try:
        api_url = "https://683eea301cd60dca33dd8cb2.mockapi.io/competitor_prices"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {item['product_id']: item['competitor_price'] for item in data}
    except Exception as e:
        print(f"Error getting competitor prices: {str(e)}")
        return {}

def apply_business_rules(ml_price, product, competitor_price):
    # Rule 1: Low inventory override
    if product['inventory'] < 5:  # Critical threshold
        ml_price = min(ml_price * 1.3, product['base_price'] * 1.5)
    
    # Rule 2: Competitor undercutting
    if competitor_price and product['current_price']:
        price_diff = (product['current_price'] - competitor_price) / product['current_price']
        if price_diff > 0.2:  # Competitor undercuts by >20%
            ml_price = max(ml_price * 0.8, product['cost_price'] * 1.1)
    
    # Global constraints
    ml_price = max(ml_price, product['cost_price'] * 1.1)  # Min profit margin
    ml_price = min(ml_price, product['base_price'] * 1.5)  # Max price cap
    
    return round(ml_price, 2)