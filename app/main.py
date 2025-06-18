import googlemaps
import time
import os
import requests
import pandas as pd
import config
import math
import numpy as np
from shared_func import osmnx_func, etl_func, google_street_view_func, dynamo_func

# Set decimal precision for coordinates
DECIMAL_PLACES = 6

# Global variables for testing
gdf = None
df = None
processed_groups = []

def download_network(city):
    """Load or download the road network data based on configuration."""
    return osmnx_func.get_road_network(city)

def prepare_data(gdf,city):
    """Extract coordinates, group data, and prepare for processing."""
    df = osmnx_func.extract_coordinates(gdf)
    df["coordinates"] = df["coordinates"].apply(lambda x: (round(x[0], DECIMAL_PLACES), round(x[1], DECIMAL_PLACES)))
    df["group"] = df["start_node"].astype(str) + "-" + df["end_node"].astype(str)
    df["city"] = city
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

def main():
    global gdf, df  # Define as global to access after testing
    # Load or download network data
    gdf = download_network(city)

    # Prepare DataFrame and set up coordinates/groups
    df = prepare_data(gdf,city)

    # Process data by cleaning, sorting, and assigning order
    df = process_data(df)
    
    # Process images and upload to S3
    process_images_for_groups(df)

    print("Processing complete.")

# Run main function
if __name__ == "__main__":
    main()

