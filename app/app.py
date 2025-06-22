import logging
import os
import pandas as pd
import streamlit as st
from PIL import Image
import config
from shared_func import osmnx_func, etl_func, google_street_view_func, dynamo_func
import unicodedata
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

DECIMAL_PLACES = 6  # Adjust as needed

# Streamlit page config
st.set_page_config(page_title="GovSananga", layout="wide")

# --- Cognito Login Function --- #
def cognito_login():
    st.subheader("Login")
    username = st.text_input("Email", key="username")
    password = st.text_input("Password", type="password", key="password")
    login_status = st.empty()

    if st.button("Login"):
        try:
            response = requests.post(
                "https://hewx1kjfxh.execute-api.us-east-1.amazonaws.com/prod/dataiesb-auth",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )

            if response.ok:
                data = response.json()
                st.session_state["authenticated"] = True
                st.session_state["idToken"] = data.get("idToken", "")
                login_status.success("Login successful!")
                return True
            else:
                login_status.error(response.json().get("message", "Login failed."))
        except Exception as e:
            login_status.error(f"Error: {str(e)}")
    return False

# --- Auth Check --- #
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    if not cognito_login():
        st.stop()

# --- App UI --- #
st.title("GovSananga")
st.image(Image.open(config.img_repo_path))
st.write("Enter a place name to view its road network map.")

# User Input
place = st.text_input("Place name:", "")

# --- Functions --- #
def download_network(place):
    logging.debug(f"Downloading road network for: {place}")
    return osmnx_func.get_road_network(place)

def normalize_place(s):
    try:
        if "/" in s:
            s = s.split("/")[1]
        normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8")
        return normalized.strip().lower().replace(" ", "_")
    except Exception:
        return ""

def prepare_data(gdf, place):
    df = osmnx_func.extract_coordinates(gdf)
    df["coordinates"] = df["coordinates"].apply(
        lambda x: (round(x[0], DECIMAL_PLACES), round(x[1], DECIMAL_PLACES))
    )
    normalized = normalize_place(place)
    df["place"] = normalized
    df["group"] = df.apply(lambda row: f"{normalized}-{row['start_node']}-{row['end_node']}", axis=1)

    logging.debug("Prepared DataFrame:\n%s", df.head())
    return df

def process_data(df):
    df = etl_func.drop_duplicates(df)
    df = etl_func.assign_total(df)
    df = df.sort_values(by=["total_coordinates"], ascending=False)
    df = etl_func.add_order_column_in_all_groups(df)
    df['order'] = df["order"].astype(int)
    df = df.sort_values(by=["total_coordinates", "order"], ascending=[False, True])
    df = etl_func.assign_next_coordinates(df)
    df = etl_func.assign_previous_coordinates(df)
    logging.debug(f"Processed DataFrame: \n{df.head()}")
    return df

def process_images_for_groups(df):
    for i, group_name in enumerate(df["group"].unique()):
        if config.limit_loop is not None and i >= config.limit_loop:
            break
        group_df = df[df["group"] == group_name].copy()
        logging.debug(f"Processing group {group_name} ({i+1})")
        filtered_df = google_street_view_func.automate_street_view_images(df, group_name, config.bucket_name, config.region_name)
        logging.debug(f"Filtered DataFrame for {group_name}: \n{filtered_df.head()}")
        dynamo_func.insert_df_to_dynamodb(df=filtered_df, table_name=config.dynamo_tbl_1)

# --- Main Logic --- #
if st.button("Generate Map"):
    if place:
        try:
            st.write(f"Processing for: **{place}**...")
            gdf = download_network(place)
            image_path = config.img_map_path
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            osmnx_func.plot_realistic_road_network(gdf, place, output_image=image_path)

            if os.path.isfile(image_path):
                st.image(Image.open(image_path), caption=f"Road Network Map for {place}", use_column_width=True)
                logging.debug("Map image displayed successfully.")
            else:
                st.error("Failed to generate the road network map.")
                logging.error("Image file not found after generation.")

            df = prepare_data(gdf, place)
            df = process_data(df)
            process_images_for_groups(df)
            logging.info("Processing complete.")
        except Exception as e:
            logging.error(f"Error processing place {place}: {e}")
            st.error(f"An error occurred: {e}")

