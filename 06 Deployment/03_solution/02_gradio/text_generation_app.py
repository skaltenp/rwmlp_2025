import os
import json
from pickle import load

from PIL import Image
import requests

from gradio import ChatMessage
import gradio as gr

# every Gradio app needs a function that will be called when the user interacts with the interface
# in this case, we will generate text using a FastAPI endpoint

# generating the text based on a prompt, when the user submits a message
# the gr.update(value="") is used to clear the input field after submission
# this is a simple hack to make the UI more user-friendly
# don't forget to make sure that the inp_text is variable of the submit output

# if you have chatbot interfaces you should use the ChatMessage Type
# There are other components that can also push messages to the interface but with this you can handle history and roles easily
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
# you start with a gr.Blocks() context manager
# and then you can add components to it
# like gr.Markdown for text, gr.Chatbot for a chat interface, gr.Textbox for input fields, etc.
# you can also use gr.Row and gr.Column to create a grid layout
# for Dataframes that shall be changable you can use gr.Dataframe
# for more information on the components, check the gradio documentation
# https://gradio.app/docs/
with gr.Blocks() as demo:
    gr.Markdown("# This is a heavily amazing Gradio app connecting with FastAPI")
    chatbot = gr.Chatbot(
        type="messages",
    )
    inp_key = gr.Textbox(
        lines=1, label="API Key", placeholder="Enter your API key here"
    )
    inp_secret = gr.Textbox(
        lines=1, label="API Secret", placeholder="Enter your API secret here"
    )
    inp_text = gr.Textbox(lines=1, label="Chat Message")
    inp_text.submit(generate, [inp_key, inp_secret, inp_text, chatbot], [chatbot, inp_text])

demo.launch()