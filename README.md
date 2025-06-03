# Dynamic Pricing System

A sophisticated dynamic pricing system that uses machine learning to optimize product prices based on historical sales data, competitor prices, and market conditions.

## System Architecture

### Backend (Flask + SQLAlchemy)
- **Flask**: Web framework for handling API requests
- **SQLAlchemy**: ORM for database operations
- **Flask-RESTX**: API documentation and request/response validation
- **Flask-CORS**: Cross-origin resource sharing support

### Frontend (React)
- **React**: Frontend framework
- **Chart.js**: Data visualization
- **React-Chartjs-2**: React wrapper for Chart.js

### Machine Learning Pipeline
- **scikit-learn**: Machine learning library
- **pandas**: Data manipulation
- **numpy**: Numerical computations

### Database
- **SQLite**: Lightweight database for storing product and sales data

## Features

1. **Dynamic Pricing Algorithm**
   - Multi-objective optimization for revenue maximization
   - Competitor price analysis
   - Inventory level consideration
   - Customer rating impact

2. **Machine Learning Integration**
   - Random Forest Regressor for price prediction
   - Feature engineering for time-based patterns
   - Historical data analysis
   - Price elasticity modeling

3. **Real-time Dashboard**
   - Product catalog with current and adjusted prices
   - Sales and inventory trends
   - Competitor price comparison
   - Interactive price updates

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm 6+

### Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. Start the Flask server:
```bash
python app.py
```

### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## API Documentation

### Endpoints

#### GET /api/dashboard
Returns dashboard data including products, prices, and metrics.

**Response:**
```json
[
  {
    "id": "string",
    "name": "string",
    "current_price": number,
    "adjusted_price": number,
    "inventory": number,
    "sales": number,
    "competitor_price": number
  }
]
```

#### POST /api/pricing/update
Updates prices for all products based on ML predictions.

**Response:**
```json
{
  "message": "string",
  "updates": [
    {
      "product_id": "string",
      "new_price": number
    }
  ]
}
```

#### GET /api/products
Returns all products.

**Response:**
```json
[
  {
    "product_id": "string",
    "base_price": number,
    "cost_price": number,
    "inventory": number,
    "current_price": number,
    "sales_last_30_days": number,
    "average_rating": number,
    "category": "string"
  }
]
```

## ML Pipeline Documentation

### Feature Engineering
1. **Time-based Features**
   - Day of week
   - Month
   - Weekend indicator

2. **Price-based Features**
   - Price change percentage
   - Price volatility
   - Competitor price ratio

3. **Sales-based Features**
   - 7-day moving average
   - 30-day moving average
   - Sales trend

4. **Product Features**
   - Inventory level
   - Inventory ratio
   - Rating factor

### Model Training
1. **Data Preparation**
   - Historical data collection
   - Feature scaling
   - Missing value handling

2. **Model Configuration**
   - Random Forest Regressor
   - 200 estimators
   - Maximum depth of 10
   - Minimum samples split of 5

3. **Price Optimization**
   - Revenue maximization
   - Competitor price consideration
   - Business rule constraints

### Business Rules
1. **Price Constraints**
   - Minimum: 10% above cost price
   - Maximum: 50% above base price
   - Competitor price range: ±20%

2. **Inventory Rules**
   - Critical inventory threshold: 5 units
   - Price adjustment for low inventory

3. **Competitor Rules**
   - Price matching for significant undercutting
   - Maximum price difference: 20%

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 