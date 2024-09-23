import googlemaps
import time
import os
import requests
from shared_func import osmnx_func 
from shared_func import etl_func 
import pandas as pd
import geopandas as gpd
import config

file_name = config.gdf_file_name

if config.download_dataset_osmnx:
    gdf = osmnx_func.get_road_network("Cidade Estrutural, Distrito Federal, Brazil")
    osmnx_func.save_road_network(gdf, output_file=file_name)
else:
    gdf = osmnx_func.load_road_network(file_name=file_name)
    
gdf = osmnx_func.get_road_network("Cidade Estrutural, Distrito Federal, Brazil")

df = osmnx_func.extract_coordinates(gdf)

df["group"] = df["start_node"].astype(str) + "-" + df["end_node"].astype(str)

df = etl_func.assign_order_and_total(df)

gr_ex = df.sort_values(by=["total_coordinates","order"], ascending=False).iloc[0]["group"]

ex = df.loc[df.group == gr_ex]


