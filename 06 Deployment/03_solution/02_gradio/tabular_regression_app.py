import io
import os
import json
from pickle import load

from PIL import Image
import requests

from gradio import ChatMessage
import gradio as gr

# every Gradio app needs a function that will be called when the user interacts with the interface
# in this case, we will predict a regression value using a FastAPI endpoint

def predict(air_temperature: str, dew_temperature: str, precip_depth_1_hr: str,
            primary_use: str, sea_level_pressure: str, square_feet: str,
            wind_direction: str, wind_speed: str, year_built: str) -> str:
    
    res = requests.post(
        "http://localhost:8000/tabular_regression/",
        json={
            "air_temperature": float(air_temperature),
            "dew_temperature": float(dew_temperature),
            "precip_depth_1_hr": float(precip_depth_1_hr),
            "primary_use": primary_use,
            "sea_level_pressure": float(sea_level_pressure),
            "square_feet": float(square_feet),
            "wind_direction": float(wind_direction),
            "wind_speed": float(wind_speed),
            "year_built": int(year_built)
        },
    )
    result = res.json().get("result", "No regression result found.")
    return result


# this is an easy way to create a Gradio interface
# but I would recommend using gr.Blocks() for more complex layouts like this example
# it allows you to create a more complex layout with multiple components and interactions
gr.Interface(
    fn=predict,
    inputs=[
        gr.Textbox(label="Air Temperature", placeholder="Enter the air temperature"),
        gr.Textbox(label="Dew Temperature", placeholder="Enter the dew temperature"),
        gr.Textbox(label="Precip Depth 1 Hr", placeholder="Enter the precip depth 1 hr"),
        gr.Dropdown(
            label="Primary Use",
            choices=[
                'Education',
                'Lodging/residential',
                'Entertainment/public assembly',
                'Public services'
            ],
        ),
        gr.Textbox(label="Sea Level Pressure", placeholder="Enter the sea level pressure"),
        gr.Textbox(label="Square Feet", placeholder="Enter the square feet"),
        gr.Textbox(label="Wind Direction", placeholder="Enter the wind direction"),
        gr.Textbox(label="Wind Speed", placeholder="Enter the wind speed"),
        gr.Textbox(label="Year Built", placeholder="Enter the year built"),
    ],
    outputs=gr.Textbox(label="Regression Result"),
    examples=[
        ["24.4", "20.6", "0", "Education", "1017.1", "116607", "210", "2.1", "1975",],
        ["22.0", "18.0", "0", "Lodging/residential", "1015.0", "150000", "180", "3.0", "1980",],
    ]
).launch()
