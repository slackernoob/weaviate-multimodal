import weaviate
import weaviate.classes.config as wc

client = weaviate.connect_to_local()  # Connect with default parameters
# client.collections.delete("DemoCollection")
assert client.is_live()

client.collections.create(
        name="DemoCollection",  # The name of the collection ('MM' for multimodal)
        properties=[
            wc.Property(name="title", data_type=wc.DataType.TEXT),
            wc.Property(name="poster", data_type=wc.DataType.BLOB),
        ],
        # Define & configure the vectorizer module
        vectorizer_config=wc.Configure.Vectorizer.multi2vec_clip(
            image_fields=[wc.Multi2VecField(name="poster", weight=0.9)],    # 90% of the vector is from the poster
            text_fields=[wc.Multi2VecField(name="title", weight=0.1)],      # 10% of the vector is from the title
        ),
    )
print("Collection created")

client.close()  # Close the connection & release resources