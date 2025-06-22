import googlemaps
import time
import os
import requests
import pandas as pd
import config
import math
import numpy as np
import config
from shared_func import osmnx_func, etl_func, google_street_view_func, dynamo_func
import unicodedata


# Set decimal precision for coordinates
DECIMAL_PLACES = 6

# Global variables for testing
gdf = None
df = None
processed_groups = []

def download_network(place):
    """Load or download the road network data based on configuration."""
    print(f"[INFO] Downloading road network for: {place}")
    return osmnx_func.get_road_network(place)

def prepare_data(gdf, place):
    """Extract coordinates, group data, and prepare for processing."""
    print("[INFO] Extracting coordinates...")
    df = osmnx_func.extract_coordinates(gdf)
    print(f"[DEBUG] Extracted {len(df)} rows with coordinates.")

    # Safely extract and round the first coordinate in the list
    def round_first_coordinate(coord_list):
        if isinstance(coord_list, list) and len(coord_list) > 0:
            x, y = coord_list[0]
            return (round(x, DECIMAL_PLACES), round(y, DECIMAL_PLACES))
        return (None, None)

    df["coordinates"] = df["coordinates"].apply(round_first_coordinate)
    df["group"] = df["start_node"].astype(str) + "-" + df["end_node"].astype(str)
    place = normalize_place(place)
    print("place:",place)
    df["place"] = place
    df["group"] = df["place"] + "-" + df["start_node"].astype(str) + "-" + df["end_node"].astype(str)

    print(f"[DEBUG] Prepared data with unique groups: {df['group'].nunique()}")
    return df

def process_data(df):
    """Perform data cleaning, ordering, and sorting."""
    print("[INFO] Cleaning and processing data...")
    df = etl_func.drop_duplicates(df)
    print(f"[DEBUG] After dropping duplicates: {len(df)} rows")
    df = etl_func.assign_total(df)
    df = df.sort_values(by=["total_coordinates"], ascending=False)
    df = etl_func.add_order_column_in_all_groups(df)
    df['order'] = df["order"].astype(int)
    df = df.sort_values(by=["total_coordinates", "order"], ascending=[False, True])
    df = etl_func.assign_next_coordinates(df)
    df = etl_func.assign_previous_coordinates(df)

    print("[DEBUG] Data processing complete.")
    return df

def process_images_for_groups(df):
    """Iterate through unique groups, process images, and upload to S3."""
    print("[INFO] Starting image processing for groups...")
    global filtered_df  # Define as global to access after testing
    for i, group_name in enumerate(df["group"].unique()):
        if config.limit_loop is not None and i >= config.limit_loop:
            print(f"[INFO] Reached limit_loop={config.limit_loop}, stopping.")
            break
        print(f"[INFO] Processing group {i+1}: {group_name}")
        group_df = df[df["group"] == group_name].copy()
        filtered_df = google_street_view_func.automate_street_view_images(df, group_name,config.bucket_name,config.region)

        if filtered_df is None or filtered_df.empty:
            print(f"[WARN] No data returned for group: {group_name}, skipping.")
            continue
        dynamo_func.insert_df_to_dynamodb(df=filtered_df, table_name=config.dynamo_tbl_1)
        print(f"[DEBUG] Finished processing and uploading for group: {group_name}")

def normalize_place(s):
    """Normalize a place name from raw input or S3-style path."""
    try:
        # Extract if it's a path
        if "/" in s:
            s = s.split("/")[1]
        # Normalize accents, lowercase, trim, and replace spaces
        normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8")
        return normalized.strip().lower().replace(" ", "_")
    except Exception:
        return ""


def main():
    global gdf, df  # Define as global to access after testing

    place = "Cidade Estrutural - Scia"
    place = "Gardênia Azul"

    print("[INFO] Starting main pipeline...")
    gdf = osmnx_func.get_road_network(place)
    print("[INFO] Road network loaded.")

    df = prepare_data(gdf, place)
    print("[INFO] Data prepared.")

    df = process_data(df)
    print("[INFO] Data processed.")

    process_images_for_groups(df)
    print("[INFO] Image processing complete.")

    print("[INFO] Processing complete.")

if __name__ == "__main__":
    main()

