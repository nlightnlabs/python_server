import requests
import pandas as pd

# Define the API endpoint URL
url = 'http://localhost:8000/python/db/table'  # Adjust the port as necessary

# Prepare the data to send in the POST request
data = {
    "tableName": "users",  # Replace with your actual table name
    "dbName": "main"     # Optional: replace with your actual database name
}

# Make the POST request to the Flask API
try:
    response = requests.post(url, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the JSON response
        result = response.json()
        print("Data retrieved successfully:")
        print(result)  
    else:
        print(f"Error: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

data = pd.DataFrame(response)
data
