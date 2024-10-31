import requests
import json

# Define the endpoint URL and your data
url = 'https://nlightnlabs.net/python/db/tableDataFrame'  # Adjust the port as necessary
data = {
    "tableName": "staff_data",
    "dbName": "wis"  # Optional, can be omitted
}

# Make the POST request to the Flask API
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Process the JSON response
    result_df = response.json()
    print("DataFrame Retrieved Successfully:")
    print(result_df)  # or handle the DataFrame as needed
else:
    print(f"Error: {response.status_code} - {response.text}")
