import googlemaps
import time
import os
import requests
from shared_func import osmnx_func 
from shared_func import etl_func 
from shared_func import google_street_view_func
import pandas as pd
import geopandas as gpd
import config
import math
import numpy as np
from geopy.distance import great_circle


file_name = config.gdf_file_name

if config.download_dataset_osmnx:
    gdf = osmnx_func.get_road_network("Cidade Estrutural, Distrito Federal, Brazil")
    osmnx_func.save_road_network(gdf, output_file=file_name)
else:
    gdf = osmnx_func.load_road_network(file_name=file_name)
    
# Display the updated DataFrame
gdf = osmnx_func.get_road_network("Cidade Estrutural, Distrito Federal, Brazil")

df = osmnx_func.extract_coordinates(gdf)

decimal_places = 6

df["coordinates"] = df["coordinates"].apply(lambda x: (round(x[0], decimal_places), round(x[1], decimal_places)))

df["group"] = df["start_node"].astype(str) + "-" + df["end_node"].astype(str)



dfall = df.copy()

df = etl_func.drop_duplicates(df)

df = etl_func.assign_total(df)
df = df.sort_values(by=["total_coordinates"], ascending=False)

lst = df["group"].unique().tolist()

#df = df[df["group"] == lst[1]]

# Apply the function to add the "order" column
df = etl_func.add_order_column_in_all_groups(df)
df['order'] = df["order"].astype(int)

df = df.sort_values(by=["total_coordinates", "order"], ascending=[False, True])

df = etl_func.assign_next_coordinates(df)
df = etl_func.assign_previous_coordinates(df)

for i, gr in enumerate(df["group"].unique()):
    group_df = df[df["group"] == gr].copy()  # Extract group-specific DataFrame
    google_street_view_func.automate_street_view_images(df,gr)
    if i > 2:
        break

df.drop(columns=["name","start_node","end_node","total_coordinates","summary"],inplace=True)
