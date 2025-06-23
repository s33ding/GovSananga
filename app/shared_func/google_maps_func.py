import folium
from folium.plugins import Fullscreen
import boto3
from io import BytesIO
import boto3
from shared_func.secret_manager_func import get_secret

google_api_key = get_secret("s33ding").get("gcp")

def plot_with_google_basemap(gdf, place_name, bucket_name):
    """
    Plots a road network GeoDataFrame over Google Maps and uploads HTML directly to S3.

    Parameters:
        gdf (GeoDataFrame): Road network data.
        place_name (str): Normalized place name (used as S3 folder).
        bucket_name (str): Destination S3 bucket.
        google_api_key (str): Google Maps API key.
    """

    if google_api_key is None:
        raise ValueError("Google Maps API key is required.")

    # Reproject to WGS84
    gdf = gdf.to_crs(epsg=4326)
    bounds = gdf.total_bounds
    center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    # Create Folium map
    m = folium.Map(location=center, zoom_start=14, control_scale=True, tiles=None)
    Fullscreen().add_to(m)

    # Add Google basemap
    folium.TileLayer(
        tiles=f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_api_key}",
        attr="Google Maps",
        name="Google Maps",
        overlay=True,
        control=True
    ).add_to(m)

    # Add road network
    folium.GeoJson(
        gdf,
        name="Road Network",
        style_function=lambda x: {
            'color': '#3366cc',
            'weight': 2,
            'opacity': 0.8
        }
    ).add_to(m)

    folium.LayerControl().add_to(m)

    # Render to HTML in-memory
    html_buffer = BytesIO()
    html_content = m.get_root().render()
    html_buffer.write(html_content.encode("utf-8"))
    html_buffer.seek(0)

    # Upload to S3
    s3_key = f"{place_name}/google_maps_interactive_map.html"
    s3 = boto3.client("s3")
    s3.put_object(
        Body=html_buffer,
        Bucket=bucket_name,
        Key=s3_key,
        ContentType="text/html"
    )

    print(f"[INFO] Uploaded HTML map to s3://{bucket_name}/{s3_key}")

