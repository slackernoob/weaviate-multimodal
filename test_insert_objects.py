import requests
import json
import os
import base64

# Helper function to convert file to base64 representation
def to_base64(url_or_path):
    if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
        # Handle URL
        image_response = requests.get(url_or_path)
        content = image_response.content
    elif os.path.exists(url_or_path):
        # Handle local file path
        with open(url_or_path, 'rb') as image_file:
            content = image_file.read()
    else:
        raise ValueError("The provided string is neither a valid URL nor a local file path.")
    
    return base64.b64encode(content).decode("utf-8")

directory = "./simple_images/cat/"
source = os.listdir(directory)
payload = {
    "collection_name": "DemoCollection",
}

objs = []
for src_obj in source:
    obj = {}
    obj["name"] = os.path.splitext(src_obj)[0]
    obj["image"] = to_base64(directory+src_obj)
    objs.append(obj)

payload["objects"] = objs
# print(payload["objects"][0]['name'])

# URL of your FastAPI endpoint
url = "http://localhost:8000/insert_objects"

try:
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Print the response from the server
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(f"Error sending request: {e}")