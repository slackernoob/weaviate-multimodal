from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import weaviate
import weaviate.classes as wvc
import logging

VLM_API_BASE = "http://10.255.252.128:8001/v1"

class Item(BaseModel):
    text: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None

class InsertRequest(BaseModel):
    collection_name: str
    objects: List[Item]

class nearbySearchRequest(BaseModel):
    collection_name: str
    query: str
    image: Optional[str] = None

class collectionRequest(BaseModel):
    collection_name: str

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create_collection")
async def create_collection(request: collectionRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name
    # logging.info("Request headers: %s", request.headers)
    # logging.info("Request body: %s", await request.json())

    if client.collections.exists(collection_name):
        client.close()
        raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' already exists.")
    
    client.collections.create(
        name=collection_name,
        properties=[
            wvc.config.Property(name="name", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="image", data_type=wvc.config.DataType.BLOB),
            wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="b64image", data_type=wvc.config.DataType.TEXT),
        ],
        # Define & configure the vectorizer module
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
            image_fields=[wvc.config.Multi2VecField(name="image", weight=0)],
            text_fields=[wvc.config.Multi2VecField(name="name", weight=0),
                         wvc.config.Multi2VecField(name="b64image", weight=0),
                         wvc.config.Multi2VecField(name="text", weight=1.0),],
        ),
    )
    client.close()
    return {"status": f"Collection {collection_name} created successfully"}
    # f"Collection {collection_name} created successfully"

@app.post("/delete_collection")
def delete_collection(request: collectionRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name

    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
        client.close()
        return {"status": f"Collection {collection_name} deleted successfully"}
    client.close()
    raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' does not exist.")
    
    

@app.post("/insert_objects")
def insert_objects(request: InsertRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name
    collection = client.collections.get(collection_name)
    objects = request.objects

    with collection.batch.dynamic() as batch:
        for item in objects:
            weaviate_obj = {}
            base64_image = item.image
            # Get image captions from the VLM endpoint
            vlm_response = requests.post(
                VLM_API_BASE + "/chat/completions",
                json={
                    "model": "llava",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                # {"type": "text", "text": "List out the keywords in this image"},
                                {"type": "text", "text": "List out the top 10 keywords in this image, without duplicates, in this format: keyword1 keyword2 keyword3"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=None,
            )
            
            # captions = "it is a beautiful Friday afternoon"
            captions = vlm_response.json()['choices'][0]['message']['content']

            if item.text is not None:
                weaviate_obj["text"] = item.text + " " + captions 
            else:
                weaviate_obj["text"] = captions
            
            if item.name is not None:
                weaviate_obj["name"] = item.name
            if item.image is not None:
                weaviate_obj["image"] = item.image
                weaviate_obj["b64image"] = item.image
            batch.add_object(properties=weaviate_obj)

    client.close()
    return {"status": "success"}


@app.post("/nearby_search")
def nearby_search(request: nearbySearchRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name
    collection = client.collections.get(collection_name)
    query = request.query

    # Check if collection is empty or not
    count = 0
    for item in collection.iterator():
        count += 1
        break
    if count == 0:
        print("count is zero")
        raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' is empty.")


    base64_image = request.image
    print(len(base64_image))
    # Get image captions from the VLM endpoint
    if base64_image != None and len(base64_image) > 0:
        vlm_response = requests.post(
            VLM_API_BASE + "/chat/completions",
            json={
                "model": "llava",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "List out the top 10 keywords in this image, without duplicates, in this format: keyword1 keyword2 keyword3"},
                            # {"type": "text", "text": "What's in this image? Include all the text headers found in the image in the response"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
            },
            timeout=None,
        )
        print("test")
        print(vlm_response.json())
        captions = vlm_response.json()['choices'][0]['message']['content']
    else:
        captions = ""
    # captions = "it is a beautiful Friday afternoon"
    
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
