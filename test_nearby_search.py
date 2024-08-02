import requests
import json
import base64
import os
from PIL import Image
from io import BytesIO

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


# Modify according to test query
directory = "./simple_images/orange-cat.jpg"
base64_string = to_base64(directory)
collection_name = "DemoCollection1"
query = "Green Action for Communities Movement"

# URL of FastAPI endpoint
url = "http://localhost:8000/nearby_search"
 
payload = {
    "collection_name" : collection_name,
    "query": query,
    # "image": ,#base64_string,
    }

try:
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url,
                             headers=headers,
                             data=json.dumps(payload),
                             timeout=None)

    # print(response.status_code)
    if response.status_code == 400:
        print(response.json()['detail'])

    response_data = response.json()
    print(response_data[0]['name'])
    # print(response_data[0]['b64image'])
    print(response_data[0]['text'])
    print(response_data[1]['name'])
    # print(response_data[1]['b64image'])
    print(response_data[1]['text'])
    print(response_data[2]['name'])
    # print(response_data[2]['b64image'])
    print(response_data[2]['text'])
    # for result in response_data:
    #     print("-----")
    #     print(result['text'])
    #     print("--")
        # print(result['name']) # base64 image
        
        # print("--")
        # print(result['image'])
    
    # to display the image
    encoded_image = response_data[0]['b64image']
    image_data = base64.b64decode(encoded_image)
    image = Image.open(BytesIO(image_data))
    image.show()
    
except Exception as e:
    print(f"Error sending request: {e}")
