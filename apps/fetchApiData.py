import requests
from tabulate import tabulate

def fetch_data(url):
    try:
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON data if the request was successful
            return response.json()
        else:
            # Print an error message if the request was not successful
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Print an error message if there was an exception during the request
        print(f"Error: {e}")
        return None

# Example API endpoint to fetch data from
api_url = "https://nlightnlabs.net/nlightn/db/table/industries"

# Fetch data from the API endpoint
data = fetch_data(api_url)

# Print the fetched data
if data:
    print(data)

#Format output in table format
table = tabulate(data, headers="firstrow", tablefmt="html")
print(table)