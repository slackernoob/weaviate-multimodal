import json
import requests


url = "http://localhost:8000/create_collection"

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
    # print(response.status_code)

    if response.status_code == 200:
        print(response.json()['status'])
    elif response.status_code == 400:
        print(response.json()['detail'])

except Exception as e:
    print(f"Error sending request: {e}")