import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx

def plot_realistic_road_network(gdf, place_name, output_image="realistic_road_network_map.png"):
    import os
    import matplotlib.pyplot as plt
    import contextily as ctx

    # If the output_image is a directory, convert it into a file path
    if os.path.isdir(output_image):
        print(f"[WARN] Output path '{output_image}' is a directory. Saving to 'road_map.png' inside it.")
        output_image = os.path.join(output_image, "road_map.png")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(output_image), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(f"Road Network in {place_name}", fontsize=15)

    gdf.plot(ax=ax, linewidth=0.7, color="blue", alpha=0.7)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    plt.savefig(output_image, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[INFO] Road network image saved to: {output_image}")


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
    plot_realistic_road_network(gdf, place_name, "output/road_network_map.png")

    
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

