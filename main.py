from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union
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
    image: Optional[str] = None

app = FastAPI()

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

    
    # response = {
    #     'id': 'cmpl-beadb6213adb46738fae279276bbf564',
    #     'object': 'chat.completion',
    #     'created': 1720513536,
    #     'model': 'llava',
    #     'choices': [{
    #         'index': 0,
    #         'message': {
    #             'role': 'assistant',
    #             'content': 'This image shows a pie chart with categories for sales. The chart is labeled "Sales chart" and includes four categories: Toys, Furniture, Home Decor, and Electronics. Each category has a different color and a percentage of the total sales assigned to it. The percentages are shown as follows: Toys with 28%, Furniture with 14%, Home Decor with 34%, and Electronics with 15%. The colors of the categories are blue, orange, and yellow, and the chart is presented against a white background. ',
    #             'tool_calls': []
    #         },
    #         'logprobs': None,
    #         'finish_reason': 'stop',
    #         'stop_reason': None
    #     }],
    #     'usage': {
    #         'prompt_tokens': 1196,
    #         'total_tokens': 1319,
    #         'completion_tokens': 123
    #     }
    # }    

    with collection.batch.dynamic() as batch:
        for item in objects:
            weaviate_obj = {}
            base64_image = item.image
            # Captions from the VLM endpoint
            vlm_response = requests.post(
                "http://10.255.252.128:8001/v1/chat/completions",
                json={
                    "model": "llava",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What's in this image?"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        # "url": "https://www.spotfire.com/content/dam/spotfire/images/graphics/inforgraphics/pie1.png"
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                },
            )
            # print(vlm_response.json())
            captions = vlm_response.json()['choices'][0]['message']['content']

            weaviate_obj["text"] = captions

            if item.name is not None:
                weaviate_obj["name"] = item.image
            if item.image is not None:
                weaviate_obj["image"] = item.image
            batch.add_object(properties=weaviate_obj)

    client.close()
    return {"status": "success"}




@app.post("/near_text_query")
def near_text_query(request: nearTextQueryRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name
    query = request.query

    base64_image = request.image
    # Captions from the VLM endpoint
    vlm_response = requests.post(
        "http://10.255.252.128:8001/v1/chat/completions",
        json={
            "model": "llava",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                # "url": "https://www.spotfire.com/content/dam/spotfire/images/graphics/inforgraphics/pie1.png"
                                # "url": "simple_images/sample_charts/chart1.png",
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
        },
    )
    captions = vlm_response.json()['choices'][0]['message']['content']
    collection = client.collections.get(collection_name)
    
    
    
    response = collection.query.near_text(
        query=query + captions,
        distance=0.6,
        return_metadata=wvc.query.MetadataQuery(distance=True),
        limit=3
    )
    res = []

    for o in response.objects:
        res.append(o.properties)
        # print(o.properties)
        print(o.metadata)

    return res
