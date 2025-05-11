import os
import sys
import logging
import time
import datetime
import json
import requests
import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError
from watchdog.observers import Observer
from sqlalchemy import create_engine
from watchdog.events import FileSystemEvent, FileSystemEventHandler


class OverrideHandler(FileSystemEventHandler):

    def extract_and_transform(self, file_path):
        meter_data = None
        weather_data = pd.DataFrame(columns=["timestamp", "site_id", "air_temperature", "cloud_coverage", "dew_temperature", "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed", ])

        meter_data = pd.DataFrame(columns=["timestamp", "site_id", "building_id", "meter" ,"meter_reading"])
        
        data = pd.DataFrame(columns=["timestamp", "site_id", "building_id", "meter_id" ,"meter_reading"])
        if file_path.endswith(".csv") and "meter_reading" in file_path:
            try:
                data = pd.read_csv(file_path)
                if len(data) > 0: 
                    row = file_path.replace(".csv", "").split("dso_data/")[-1].split("/")
                    row.remove("meter_reading")
                    data[["site_id", "building_id"]] = row
                    data = data.melt(
                        id_vars=["timestamp", "site_id", "building_id", ], 
                        var_name="meter_id", 
                        value_name="meter_reading",
                    )
                    data["meter_id"] = data["meter_id"].apply(lambda x: int(x.split("_")[-1]))
                    data = data[["timestamp", "site_id", "building_id", "meter_id", "meter_reading",]].copy()
                    data.timestamp = data.timestamp.astype(str)
            except EmptyDataError as e:
                print(e)
        elif file_path.endswith(".jsonl"):
            try:
                data = pd.read_json(file_path, lines=True)
                if len(data) > 0:    
                    data[["site_id", "building_id", "meter_id"]] = file_path.replace(".jsonl", "").split("dso_data/")[-1].split("/")
                    data = data[["timestamp", "site_id", "building_id", "meter_id", "meter_reading",]].copy()
                    data.timestamp = data.timestamp.astype(str)
            except Exception as e:
                print(e)
        if len(data) > 0:
            meter_data = data
            meter_data["meter_id"] = meter_data["meter_id"].astype(int)
            meter_data["building_id"] = meter_data["building_id"].astype(int)
            meter_data = meter_data.rename(columns={"meter_id": "meter"})
            weather_data_list = []
            for site_id in meter_data.site_id.unique():
                res_hist = requests.get("http://131.234.154.105:33100/forecast/", params={'site': site_id, 'day': meter_data.timestamp.min().split()[0]})
                content = json.loads(res_hist.content)["results"]
                weather = pd.DataFrame.from_dict(content)
                weather_data_list.append(weather)
            weather_data = pd.concat(weather_data_list)
            if len(weather_data) < 1:
                weather_data = pd.DataFrame(columns=["timestamp", "site_id", "air_temperature", "cloud_coverage", "dew_temperature", "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed", ])
        
        engine = create_engine(self.URL)
        with engine.begin() as connection:
            weather_data.to_sql(name="weather_data", con=connection, if_exists='append', index=False)
            meter_data_old = pd.read_sql_table("meter_data", con=connection)
            meter_data_old = meter_data_old.sort_values(by=["timestamp"]).drop_duplicates(subset=["site_id", "building_id"], keep="last")
            site_id = meter_data.site_id.unique()[0]
            building_id = meter_data.building_id.unique()[0]
            timestamp = meter_data_old.timestamp.max()
            meter_data[
                (meter_data["site_id"] == site_id) &
                (meter_data["building_id"] == building_id) &
                (meter_data["timestamp"] > timestamp)
            ].to_sql(name="meter_data", con=connection, if_exists='append', index=False)

    def __init__(self):
        super(OverrideHandler, self).__init__()
        
        URL = f"sqlite:///ELT.db"
        self.URL = URL

    def on_modified(self, event):
        print(f"Path modified: {event.src_path}")
        self.extract_and_transform(event.src_path)

path = "dso_data"
event_handler = OverrideHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()
try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()