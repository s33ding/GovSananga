import osmnx as ox
import pandas as pd
import geopandas as gpd


def get_road_network(place_name, output_file="roads.geojson"):
    """
    Retrieve the road network for a given place and save it to a GeoJSON file.
    
    Parameters:
    place_name (str): The name of the place to retrieve the road network for.
    output_file (str): The file path where the GeoJSON will be saved. Default is 'roads.geojson'.
    """
    # Retrieve road network from OSM
    G = ox.graph_from_place(place_name, network_type="all")
    
    # Get road edges (links between intersections)
    gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
    
    return gdf

def save_road_network(gdf, output_file="roads.geojson"):
    # Save to a GeoJSON or shapefile
    gdf.to_file(output_file, driver="GeoJSON")

def load_road_network(file_name="roads.geojson"):
    return gpd.read_file(file_name)

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

