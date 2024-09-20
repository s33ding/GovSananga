import osmnx as ox
import pandas as pd
import geopandas as gpd

# Load the GeoDataFrame (assuming the file is a GeoDataFrame-compatible format like GeoJSON or Shapefile)

file_name = "estrutural_roads.geojson"

gdf = gpd.read_file(file_name)

# List to hold the data
data = []

# Loop over each geometry in the GeoDataFrame
for idx, row in gdf.iterrows():
    geom = row['geometry']
    u = row['u']
    v = row['v']
    key = row['key']

    # Check if the geometry is a LineString and extract coordinates
    if geom.geom_type == 'LineString':
        for coord in geom.coords:
            # Revert x and y
            x, y = coord

            # Append a new row to the data list
            data.append({
                'u': u,
                'v': v,
                'x': x,
                'y': y,
                'geometry_index': idx  # To keep track of the original geometry
            })

# Create the DataFrame from the list of data
df = pd.DataFrame(data)



