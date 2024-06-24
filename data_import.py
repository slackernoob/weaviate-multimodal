import base64
import os
import requests
import weaviate

# def url_to_base64(url):
#     image_response = requests.get(url)
#     content = image_response.content
#     return base64.b64encode(content).decode("utf-8")

def url_to_base64(url_or_path):
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

client = weaviate.connect_to_local()  # Connect with default parameters
assert client.is_live()

collection = client.collections.get("DemoCollection")
# source_objects = [{"title": "comparison inflation rates", 
#                    "description": "comparison of inflation rates of Singapore and the World from 2000 to 2022",
#                    "poster_path": "./source_objects/pg5_comparison_inflation_rates.png"},
#                    {"title": "income growth",
#                     "description": "real annualised change in average monthly household income from work per member (2013 to 2023)",
#                     "poster_path": "./source_objects/pg35_income_growth_by_quintile.png"}
#                     ]

source_objects = os.listdir("./simple_images/dog/")

with collection.batch.dynamic() as batch:
    for src_obj in source_objects:
        path = "./simple_images/dog/" + src_obj
        poster_b64 = url_to_base64(path)
        weaviate_obj = {
            "title": src_obj,
            # "description": src_obj["description"],
            "poster": poster_b64  # Add the image in base64 encoding
        }

        # The model provider integration will automatically vectorize the object
        batch.add_object(
            properties=weaviate_obj,
            # vector=vector  # Optionally provide a pre-obtained vector
        )
print("data imported")
client.close()  # Close the connection & release resources
