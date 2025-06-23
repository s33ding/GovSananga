import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from io import BytesIO
import boto3
import geopandas as gpd

def plot_road_network(bucket_name,place_name):

    s3 = boto3.client("s3")
    geojson_key = f"{place_name}/roads.geojson"

    try:
        # Load GeoJSON from S3
        s3 = boto3.client("s3")
        geojson_obj = s3.get_object(Bucket=bucket_name, Key=geojson_key)
        gdf = gpd.read_file(BytesIO(geojson_obj["Body"].read()))
        print(f"[INFO] Loaded GeoJSON from s3://{bucket_name}/{geojson_key}")
    except Exception as e:
        print(f"[ERROR] Could not load GeoJSON: {e}")
        return

    # Plot to in-memory buffer
    image_key = f"{place_name}/road_network_map.png"
    try:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_title(f"Road Network in {place_name}", fontsize=15)
        gdf.plot(ax=ax, linewidth=0.7, color="blue", alpha=0.7)
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)

        # Upload PNG buffer to S3
        s3.upload_fileobj(buffer, bucket_name, image_key, ExtraArgs={"ContentType": "image/png"})
        print(f"[INFO] Uploaded image to s3://{bucket_name}/{image_key}")

    except Exception as e:
        print(f"[ERROR] Failed to generate or upload map: {e}")




def get_road_network(bucket_name,place_name,place_name_normalized):
    """
    Retrieve the road network from OSM and upload it to S3 as GeoJSON.
    Also triggers a PNG map upload via plot_realistic_road_network.
    """
    # S3 settings
    geojson_key = f"{place_name_normalized}/roads.geojson"

    try:
        # Download road network from OpenStreetMap
        G = ox.graph_from_place(place_name, network_type="all")
        gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
        print(f"[INFO] Retrieved road network for: {place_name}")
    except Exception as e:
        print(f"[ERROR] Could not fetch OSM data for {place_name}: {e}")
        return None

    try:
        # Convert GeoDataFrame to GeoJSON (in memory)
        geojson_buffer = BytesIO()
        gdf.to_file(geojson_buffer, driver="GeoJSON")
        geojson_buffer.seek(0)

        # Upload GeoJSON to S3
        s3 = boto3.client("s3")
        s3.upload_fileobj(geojson_buffer, bucket_name, geojson_key, ExtraArgs={"ContentType": "application/geo+json"})
        print(f"[INFO] Uploaded GeoJSON to s3://{bucket_name}/{geojson_key}")
    except Exception as e:
        print(f"[ERROR] Failed to upload GeoJSON: {e}")
        return None

    # Now generate and upload the map PNG
    plot_road_network(bucket_name,place_name_normalized)

    return gdf


def save_road_network(gdf, output_file="roads.geojson"):
    # Save to a GeoJSON or shapefile
    gdf.to_file(output_file, driver="GeoJSON")

def extract_coordinates(gdf):
    # List to hold the data
    data = []

    # Loop over each geometry in the GeoDataFrame
    for idx, row in gdf.iterrows():
        geom = row['geometry']
        name = row['name']

        # Safely access 'u', 'v', and 'key' if they exist
        u = idx[0]
        v = idx[1]
        key = idx[2]

        # Check if the geometry is a LineString and extract coordinates
        if geom.geom_type == 'LineString':
            for coord in geom.coords:
                # Revert x and y
                x, y = coord

                # Append a new row to the data list with (x, y) as a tuple
                data.append({
                    'start_node': u,
                    'end_node': v,
                    'coordinates': (y, x),  # Combine x and y into a single tuple
                    'name': name  # Combine x and y into a single tuple
                })

    # Create the DataFrame from the list of data
    df = pd.DataFrame(data)
    return df

