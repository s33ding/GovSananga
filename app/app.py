import googlemaps
import time
import os
import requests
import pandas as pd
import config
import math
import numpy as np
from shared_func import osmnx_func, etl_func, google_street_view_func, dynamo_func
import json
import subprocess
import json
import pandas as pd
import streamlit as st
import os
from PIL import Image

def prepare_data(gdf):
    """Extract coordinates, group data, and prepare for processing."""
    df = osmnx_func.extract_coordinates(gdf)
    df["coordinates"] = df["coordinates"].apply(lambda x: (round(x[0], DECIMAL_PLACES), round(x[1], DECIMAL_PLACES)))
    df["group"] = df["start_node"].astype(str) + "-" + df["end_node"].astype(str)
    return df

def process_data(df):
    """Perform data cleaning, ordering, and sorting."""
    df = etl_func.drop_duplicates(df)
    df = etl_func.assign_total(df)
    df = df.sort_values(by=["total_coordinates"], ascending=False)
    df = etl_func.add_order_column_in_all_groups(df)
    df['order'] = df["order"].astype(int)
    df = df.sort_values(by=["total_coordinates", "order"], ascending=[False, True])
    df = etl_func.assign_next_coordinates(df)
    df = etl_func.assign_previous_coordinates(df)
    return df

def process_images_for_groups(df):
    """Iterate through unique groups, process images, and upload to S3."""
    global filtered_df  # Define as global to access after testing
    for i, group_name in enumerate(df["group"].unique()):
        if config.limit_loop is not None:
            if i >= config.limit_loop:
                break
        group_df = df[df["group"] == group_name].copy()
        filtered_df = google_street_view_func.automate_street_view_images(df, group_name)
        dynamo_func.insert_df_to_dynamodb(df=filtered_df, table_name=config.dynamo_tbl_1)


def home():
    global gdf, df
    if request.method == 'POST':
        # Get form data
        name = request.form.get('city')

        # Create a dictionary with form data
        form_data = {
            'City Name': name,
        }

        gdf = osmnx_func.get_road_network(city=name)

        image_path = os.path.join('static', 'images', 'realistic_road_network_map.png')
        osmnx_func.plot_realistic_road_network(gdf, place_name, output_image=image_path)

#        df = prepare_data(gdf)
#
#        df = process_data(df)
#
#
#        process_images_for_groups(df)

        print("Processing complete.")

    return render_template('home.html', image_path=image_path)

# Set decimal precision for coordinates
DECIMAL_PLACES = 6

# Global variables for testing
gdf = None
df = None
processed_groups = []

# Set the Streamlit page configuration
st.set_page_config(page_title="GovSananga", layout="wide")

# Title and description
st.title("GovSananga")
st.image(Image.open(config.img_repo_path))
st.write("Enter a city name to view its road network map.")

# Input form for city name
place = st.text_input("Place Name:", "")

# Button to trigger processing
if st.button("Generate Map"):
    if place:
        st.write(f"Processing for: **{place}**...")

        # Download the network data
        gdf = osmnx_func.get_road_network(place)

        # Generate the image path
        image_path = config.img_map_path

        os.makedirs(image_path, exist_ok=True)

        # Generate the road network map
        osmnx_func.plot_realistic_road_network(gdf, place, output_image=image_path)

        # Display the updated image
        if os.path.exists(image_path):
            st.image(Image.open(image_path), caption=f"Road Network Map for {city_name}", use_column_width=True)
        else:
            st.error("Failed to generate the road network map.")
    else:
        st.warning("Please enter a city name before generating the map.")

