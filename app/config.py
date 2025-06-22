
import os

city="Cidade Estrutural, Distrito Federal, Brazil"
region_name = "us-east-1"
api_key="teste"
gdf_file_name="/app/output/roads.geojson"
bucket_name = "gov-sananga"
dynamo_tbl_1 = "govSananga-main"
dynamo_tbl_2 = "govSananga-img-analysis"
region = "us-east-1"
limit_loop = 3
lambda_1_label_img="arn:aws:lambda:us-east-1:248189947068:function:govSananga-label"
gsv_fov = 65

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Docker or local setup
if os.path.exists("/.dockerenv") or os.getenv("DOCKER_ENV") == "1":
    img_repo_path = "/app/media/gpt-img-repo.webp"
    img_output_dir = "/app/static/images"
else:
    img_repo_path = os.path.join(BASE_DIR, "media", "gpt-img-repo.webp")
    img_output_dir = os.path.join(BASE_DIR, "static", "images")

# Clearly define the file name and path
img_map_filename = "realistic_road_network_map.png"
img_map_path = os.path.join(img_output_dir, img_map_filename)

