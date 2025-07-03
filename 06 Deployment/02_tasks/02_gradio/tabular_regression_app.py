import io
import os
import json
from pickle import load

from PIL import Image
import requests

from gradio import ChatMessage
import gradio as gr


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

# something to implement here
