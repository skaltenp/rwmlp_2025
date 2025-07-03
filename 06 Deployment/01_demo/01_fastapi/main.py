import io
from pickle import load
from datetime import datetime
from typing import Optional, Annotated, Union, List


from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from pydantic import BaseModel

import pandas as pd
from PIL import Image
from ollama import Client

app = FastAPI()

# defines the static files directory for e.g. images and html files
app.mount("/static", StaticFiles(directory="static"), name="static") 

# call it from everywhere in the world
origins = [
    "*"
]

# add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load the pre-trained regression model
# make sure to have the file in the same directory as this script
with open("filename.pkl", "rb") as f:
    regressor = load(f)

# create an Ollama client to interact with the Ollama API
client = Client(
    host="http://131.234.154.106:11434"
)

# Pydantic models for request bodies
class FormData(BaseModel):
    # todo here
    pass

# Pydantic model for text generation data
class TextGenerationData(BaseModel):
    # do something here
    pass

# this is your ToDo
class BuildingData(BaseModel):
    # todo here

    # this is providing an example to the OpenAPI schema
    # and based on that you can know what to model above
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    'primary_use': 'Education',
                    'square_feet': 116607,
                    'year_built': 1975.0,
                    'floor_count': None,
                    'air_temperature': 24.4,
                    'cloud_coverage': None,
                    'dew_temperature': 20.6,
                    'precip_depth_1_hr': 0.0,
                    'sea_level_pressure': 1017.1,
                    'wind_direction': 210.0,
                    'wind_speed': 2.1
                }
            ]
        }
    }

# Redirect root path to the documentation
@app.get("/")
def read_root():
    return RedirectResponse("/docs")

# Endpoint for Greenspark Retrofits!
# your ToDo
@app.post("/tabular_regression/")
async def regress(values: BuildingData):
    # to do here
    res = regressor.predict(input_data)
    return {"result": res[0]}

# Endpoint for image classification
# example on how to use form data with file upload
@app.post("/img_classification/")
async def create_upload_file(data: FormData = Form(..., media_type="multipart/form-data")):
    """Endpoint to classify an image as a cat or a dog using the Ollama API."""

    if not data.upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Datei muss ein Bild sein")
    
    # everything todo
    return {}

# Endpoint for text generation
# example on how to use form data with text input
@app.post("/text_generation/")
async def generate(data: TextGenerationData):

    # do something here

    return {}



