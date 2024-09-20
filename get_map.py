from shared_func import osmnx_func 

gdf = osmnx_func.get_road_network("Cidade Estrutural, Distrito Federal, Brazil") 
osmnx_func.save_road_network(gdf, "estrutural_roads.geojson")
