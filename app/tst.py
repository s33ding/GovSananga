import geopandas as gpd
import folium
from folium.plugins import Fullscreen
import os

def plot_with_google_basemap(gdf, place_name, output_html="road_network_google.html", google_api_key=None):
    """
    Plots a road network GeoDataFrame on top of a Google Maps basemap using Folium.

    Parameters:
        gdf (GeoDataFrame): Road network data.
        place_name (str): Name of the place (for display/logging).
        output_html (str): Output HTML file.
        google_api_key (str): Your Google Maps API key.
    """
    if google_api_key is None:
        raise ValueError("Google Maps API key is required.")

    # Ensure WGS84 for web mapping
    gdf = gdf.to_crs(epsg=4326)
    bounds = gdf.total_bounds
    center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    # Create Folium map
    m = folium.Map(location=center, zoom_start=14, control_scale=True, tiles=None)
    Fullscreen().add_to(m)

    # Add Google Maps tile layer
    folium.TileLayer(
        tiles=f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_api_key}",
        attr="Google Maps",
        name="Google Maps",
        overlay=True,
        control=True
    ).add_to(m)

    # Add GeoDataFrame to the map
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

    m.save(output_html)
    print(f"[INFO] Saved interactive map to: {output_html}")

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    # 🔧 Edit this path to point to your real file (e.g., .geojson, .shp, .gpkg)
    input_file = ""
    place_name = ""
    output_html = "" 
    google_api_key = ""

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    gdf = gpd.read_file(input_file)

    plot_with_google_basemap(
        gdf=gdf,
        place_name=place_name,
        output_html=output_html,
        google_api_key=google_api_key
    )

