from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union
import json
import logging
import uvicorn
import requests
import weaviate
import weaviate.classes as wvc

class Item(BaseModel):
    text: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None

class InsertRequest(BaseModel):
    collection_name: str
    objects: List[Item]

class nearTextQueryRequest(BaseModel):
    collection_name: str
    query: str

app = FastAPI()

# logger = logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

response = {
    'id': 'cmpl-beadb6213adb46738fae279276bbf564',
    'object': 'chat.completion',
    'created': 1720513536,
    'model': 'llava',
    'choices': [{
        'index': 0,
        'message': {
            'role': 'assistant',
            'content': 'This image shows a pie chart with categories for sales. The chart is labeled "Sales chart" and includes four categories: Toys, Furniture, Home Decor, and Electronics. Each category has a different color and a percentage of the total sales assigned to it. The percentages are shown as follows: Toys with 28%, Furniture with 14%, Home Decor with 34%, and Electronics with 15%. The colors of the categories are blue, orange, and yellow, and the chart is presented against a white background. ',
            'tool_calls': []
        },
        'logprobs': None,
        'finish_reason': 'stop',
        'stop_reason': None
    }],
    'usage': {
        'prompt_tokens': 1196,
        'total_tokens': 1319,
        'completion_tokens': 123
    }
}

@app.get("/")
def read_root():
    return {"test"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



@app.post("/insert_object")
def insert_object(request: InsertRequest):
    client = weaviate.connect_to_local()
    # client = weaviate.Client("http://localhost:8080")  # Connect to Weaviate
    collection_name = request.collection_name
    collection = client.collections.get(collection_name)
    objects = request.objects

    response = {
        'id': 'cmpl-beadb6213adb46738fae279276bbf564',
        'object': 'chat.completion',
        'created': 1720513536,
        'model': 'llava',
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': 'This image shows a pie chart with categories for sales. The chart is labeled "Sales chart" and includes four categories: Toys, Furniture, Home Decor, and Electronics. Each category has a different color and a percentage of the total sales assigned to it. The percentages are shown as follows: Toys with 28%, Furniture with 14%, Home Decor with 34%, and Electronics with 15%. The colors of the categories are blue, orange, and yellow, and the chart is presented against a white background. ',
                'tool_calls': []
            },
            'logprobs': None,
            'finish_reason': 'stop',
            'stop_reason': None
        }],
        'usage': {
            'prompt_tokens': 1196,
            'total_tokens': 1319,
            'completion_tokens': 123
        }
    }    

    # resp = requests.post(
    #     "http://10.255.252.128:8001/v1/chat/completions",
    #     json={
    #         "model": "llava",
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {"type": "text", "text": "What's in this image?"},
    #                     {
    #                         "type": "image_url",
    #                         "image_url": {
    #                             # "url": "https://www.spotfire.com/content/dam/spotfire/images/graphics/inforgraphics/pie1.png"
    #                             "url": "simple_images/sample_charts/chart1.png"
    #                         },
    #                     },
    #                 ],
    #             }
    #         ],
    #     },
    # )
    
    with collection.batch.dynamic() as batch:
        for item in objects:
            weaviate_obj = {}

            weaviate_obj["text"] = response['choices'][0]['message']['content']

            if item.name is not None:
                weaviate_obj["name"] = item.name
            if item.image is not None:
                weaviate_obj["image"] = item.image
            batch.add_object(properties=weaviate_obj)

    client.close()
    return {"status": "success"}



'''
{'id': 'cmpl-beadb6213adb46738fae279276bbf564', 
'object': 'chat.completion', 
'created': 1720513536, 
'model': 'llava', 
'choices': [{'index': 0, 
            'message': {'role': 'assistant', 
                        'content': 'This image shows a pie chart with categories for sales. The chart is labeled "Sales chart" and includes four categories: Toys, Furniture, Home Decor, and Electronics. Each category has a different color and a percentage of the total sales assigned to it. The percentages are shown as follows: Toys with 28%, Furniture with 14%, Home Decor with 34%, and Electronics with 15%. The colors of the categories are blue, orange, and yellow, and the chart is presented against a white background. ', 
                        'tool_calls': []
                        }, 
            'logprobs': None, 
            'finish_reason': 'stop', 
            'stop_reason': None
            }], 
'usage': {'prompt_tokens': 1196, 
        'total_tokens': 1319, 
        'completion_tokens': 123}}
'''
# doesnt really work, not sure why
# @app.post("/near_text_query")
# def near_text_query(request: nearTextQueryRequest):
    
    
#     client = weaviate.connect_to_local()
#     collection_name = request.collection_name
#     collection = client.collections.get(collection_name)
#     print(request.query) 
    # with collection.batch.dynamic() as batch:
#     for x in range(len(source)):
#     # for src_obj in source:
#         src_obj = source[x]
#         path = directory + src_obj
#         poster_b64 = to_base64(path)
#         weaviate_obj = {
#             # "name": src_obj,
#             "name": os.path.splitext(src_obj)[0],
#             "image": poster_b64,  # Add the image in base64 encoding
#             "text": contextual_info[x] # Optional text field for image data
#         }

#         # The model provider integration will automatically vectorize the object
#         batch.add_object(
#             properties=weaviate_obj,
#         )

# with collection_2.batch.dynamic() as batch:
#     # for src_obj in source:
#     for x in range(len(source)):
#         src_obj = source[x]
#         path = directory + src_obj
#         poster_b64 = to_base64(path)
#         weaviate_obj = {
#             # "name": src_obj,
#             "name": os.path.splitext(src_obj)[0],
#             "image": poster_b64,  # Add the image in base64 encoding
#             "text": contextual_info[x] # Optional text field for image data
#         }

#         # The model provider integration will automatically vectorize the object
#         batch.add_object(
#             properties=weaviate_obj,
#         )
        # print(" ------------------- ")
    # print(response)
    # for obj in response.objects:
    #     print(obj.properties)
    #     print(obj.metadata)
    # client.close()
    # return response
    # return {"status": "success"}