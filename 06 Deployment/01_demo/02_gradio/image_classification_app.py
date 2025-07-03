import io
import os
import json
from pickle import load

from PIL import Image
import requests

from gradio import ChatMessage
import gradio as gr

# the function to run, when the user submits an image for classification and clicks the submit button
def classify(api_key: str, api_secret: str, image: Image.Image) -> str:
    b = io.BytesIO()
    image.save(b, image.format if image.format else "JPEG")
    img_bytes = b.getvalue()
    res = requests.post(
        "http://localhost:8000/img_classification",
        files={
            "upload_file": ("image.jpg", img_bytes, "image/jpeg"),
        },
        data={
            "api_key": "",
            "api_secret": "",
        },
    )
    result = res.json().get("result", "No classification result found.")
    return result

# the amazing Gradio interface
# it will be launched when you run this script
# it allows you to really easily implement a web interface for your function
# something to implement here