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


directory = "./simple_images/orange-cat.jpg"
base64_string = to_base64(directory)


# URL of your FastAPI endpoint
url = "http://localhost:8000/near_text_query"
 
payload = {
    "collection_name" : "DemoCollection",
    "query": "",
    "image": base64_string,
    }

try:
    # Convert the payload to JSON
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    print(response.status_code)
    response_data = response.json()

    for result in response_data:
        print("-----")
        print(result['text'])
        print("--")
        # print(result['name']) # base64 image
        
        print("--")
        # print(result['image'])
        
    encoded_image = response_data[0]['name']
    image_data = base64.b64decode(encoded_image)
    image = Image.open(BytesIO(image_data))
    image.show()
    
except Exception as e:
    print(f"Error sending request: {e}")