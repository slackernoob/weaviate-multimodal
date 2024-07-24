import requests

resp = requests.post(
    "http://10.255.252.128:8001/v1/chat/completions/",
    json={
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "List out the keywords in this image"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://www.spotfire.com/content/dam/spotfire/images/graphics/inforgraphics/pie1.png"
                        },
                    },
                ],
            }
        ],
    },
)

print(resp.json())
