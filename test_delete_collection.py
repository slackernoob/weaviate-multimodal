import json
import requests


url = "http://localhost:8000/delete_collection"

payload = {
    "collection_name": "DemoCollection"
}


try:
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url,
                             headers=headers,
                             data=json.dumps(payload),
                             timeout=10)

    # Print the response from the server
    print(response.status_code)
    print(response.json())

except Exception as e:
    print(f"Error sending request: {e}")