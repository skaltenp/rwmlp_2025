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

### Some tips for the Pydantic models:
# - Use `Optional` for fields that can be null or not provided.
# - Use `UploadFile` for file uploads.
# - If you are unsure about the data types, you can use `Union` to allow multiple types.

# Pydantic models for request bodies
class FormData(BaseModel):
    api_key: str
    api_secret: str
    upload_file: Optional[UploadFile] = None

# Pydantic model for text generation data
class TextGenerationData(BaseModel):
    api_key: str
    api_secret: str
    query: Optional[str] = None

# this was your ToDo
class BuildingData(BaseModel):
    primary_use: Optional[str] = None
    square_feet: Optional[float] = None
    year_built: Optional[float] = None
    floor_count: Optional[float] = None
    air_temperature: Optional[float] = None
    cloud_coverage: Optional[float] = None
    dew_temperature: Optional[float] = None
    precip_depth_1_hr: Optional[float] = None
    sea_level_pressure: Optional[float] = None
    wind_direction: Optional[float] = None
    wind_speed: Optional[float] = None

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


# FastAPI automatically generates documentation based on the defined endpoints
# because it is amazing and uses OpenAPI under the hood

# Redirect root path to the documentation
# this is a simple way to redirect the root path to the documentation
# You can also redirect to a custom HTML page or a static file or another website where you have your user management hosted
@app.get("/")
def read_root():
    return RedirectResponse("/docs")

# Endpoint for Greenspark Retrofits!
# This endpoint is for tabular regression using the pre-trained model
# it works with an application/json body
# example request body:
# {
#     "primary_use": "Education",
#     "square_feet": 116607,
#     "year_built": 1975.0,
#     "floor_count": null,
#     "air_temperature": 24.4,
#     "cloud_coverage": null,
#     "dew_temperature": 20.6,
#     "precip_depth_1_hr": 0.0,
#     "sea_level_pressure": 1017.1,
#     "wind_direction": 210.0,
#     "wind_speed": 2.1
# }
# you can use the OpenAPI schema to generate a client for this endpoint
@app.post("/tabular_regression/")
async def regress(values: BuildingData):
    input_list = [
        values.primary_use,
        values.square_feet,
        values.year_built,
        values.floor_count,
        values.air_temperature,
        values.cloud_coverage,
        values.dew_temperature,
        values.precip_depth_1_hr,
        values.sea_level_pressure,
        values.wind_direction,
        values.wind_speed
    ]
    columns = [
        'primary_use',
        'square_feet',
        'year_built',
        'floor_count',
        'air_temperature',
        'cloud_coverage',
        'dew_temperature',
        'precip_depth_1_hr',
        'sea_level_pressure',
        'wind_direction',
        'wind_speed'
    ]
    input_data = pd.DataFrame([input_list], columns=columns)
    input_data = input_data.fillna(0)
    res = regressor.predict(input_data)
    return {"result": res[0]}

# Endpoint for image classification
# example on how to use form data with file upload
# If you have any kind of file upload combined with other form data,
# you need to use the code below including "Form(..., media_type="multipart/form-data")" to prevent "unprocessable entity" errors
@app.post("/img_classification/")
async def create_upload_file(data: FormData = Form(..., media_type="multipart/form-data")):
    """Endpoint to classify an image as a cat or a dog using the Ollama API."""

    if not data.upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Datei muss ein Bild sein")
    
    io_bytes = await data.upload_file.read()
    image = Image.open(io.BytesIO(io_bytes))
    image = image.convert("RGB")
    date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    data.upload_file.filename = f"upload/{date_time}_{data.upload_file.filename}"
    image = image.save(data.upload_file.filename)
    
    res = client.chat(
        model="gemma3:4b",
        messages=[
            {
                'role': 'user',
                'content': 'Is this image a cat or a dog? Please answer with "cat" or "dog" and nothing else.',
                'images': [data.upload_file.filename]  # Use the saved image file
            }
        ]
    )

    return {
        "result": res['message']['content']
    }

# Endpoint for text generation
# example on how to use form data with text input
# this endpoint uses the Ollama API to generate text based on a query
# example request body:
# {
#     "api_key": "your_api_key",
#     "api_secret": "your_api_secret",
#     "query": "What is the capital of France?"
# }
# you can use the OpenAPI schema to generate a client for this endpoint
@app.post("/text_generation/")
async def generate(data: TextGenerationData):

    res = client.chat(
        model="gemma3:4b",
        messages=[
            {
                'role': 'user',
                'content': data.query
            }
        ]
    )

    return {"result": res['message']['content']}