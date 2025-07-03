import os
import json
from pickle import load

from PIL import Image
import requests

from gradio import ChatMessage
import gradio as gr

# generating the text based on a prompt, when the user submits a message
def generate(api_key: str, api_secret: str, prompt: str, history: list[ChatMessage]):

    history.append({"role": "user", "content": prompt})
    res = requests.post(
        "http://localhost:8000/text_generation",
        json={
            "api_key": "",
            "api_secret": "",
            "query": prompt,
        },
    )
    history.append({"role": "assistant", "content": res.json()["result"]})
    inp_text.value = ""
    return history, gr.update(value="")

# the more amazing gradio blocks
# with that you can create a more complex layout on your own
# something to implement here
