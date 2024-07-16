from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

class nearbySearchRequest(BaseModel):
    collection_name: str
    query: str
    image: Optional[str] = None

class collectionRequest(BaseModel):
    collection_name: str

app = FastAPI()

@app.post("/create_collection")
def create_collection(request: collectionRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name

    if client.collections.exists(collection_name):
        client.close()
        raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' already exists.")
    
    client.collections.create(
        name=collection_name,
        properties=[
            wvc.config.Property(name="name", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="image", data_type=wvc.config.DataType.BLOB),
            wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
        ],
        # Define & configure the vectorizer module
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
            image_fields=[wvc.config.Multi2VecField(name="image", weight=0)],    # 70% of the vector is from the image
            text_fields=[wvc.config.Multi2VecField(name="name", weight=0),       # 10% of the vector is from the name
                        wvc.config.Multi2VecField(name="text", weight=1.0)],      # 20% of the vector is from the text
        ),
    )
    client.close()
    return {"status": "success"}

@app.post("/delete_collection")
def delete_collection(request: collectionRequest):
    client = weaviate.connect_to_local()
    collection_name = request.collection_name

    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
        client.close()
        return {"status": "success"}
    client.close()
    raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' does not exist.")
    
    

@app.post("/insert_objects")
def insert_objects(request: InsertRequest):
    client = weaviate.connect_to_local()
    # client = weaviate.Client("http://localhost:8080")  # Connect to Weaviate
    collection_name = request.collection_name
    collection = client.collections.get(collection_name)
    objects = request.objects

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
                timeout=None,
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
        timeout=None,
    )
    captions = vlm_response.json()['choices'][0]['message']['content']
    
    
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
