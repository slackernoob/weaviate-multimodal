import requests
import json

# URL of your FastAPI endpoint
url = "http://localhost:8000/near_text_query"
 
payload = {
    "collection_name" : "DemoCollection",
    "query": "Cats"
    }

try:
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Print the response from the server
    print(response.status_code)
    for o in response.objects:
        print(o.properties)
        print(o.metadata)
except Exception as e:
    print(f"Error sending request: {e}")