import weaviate

client = weaviate.connect_to_local()  # Connect with default parameters
assert client.is_live()

collection = client.collections.get("DemoCollection")

response = collection.query.near_text(
    query="angry dog",  # The model provider integration will automatically vectorize the query
    limit=1
)

for obj in response.objects:
    print(obj.properties["title"])

    
client.close()  # Close the connection & release resources
