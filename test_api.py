import requests

def test_dashboard_endpoint():
    try:
        response = requests.get('http://localhost:5000/api/dashboard')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure Flask is running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_dashboard_endpoint() 