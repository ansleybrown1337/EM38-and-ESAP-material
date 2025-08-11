# Created by AJ Brown
# Date: 10 August 2025
'''
Tool to convert latitude and longitude coordinates (WGS84) from a CSV file to UTM 
Zone 13N coordinates. This is useful when running programs like ESAP for response
surface sampling design generation.
'''

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Load CSV
df = pd.read_csv(r"C:\Users\AJ-CPU\Downloads\ndvi_ndre_merged.csv")

# 2. Create geometry column
# NOTE: lon = X, lat = Y
geometry = [Point(xy) for xy in zip(df["lat"], df["long"])]


# 3. Create GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # WGS84

# 4. Convert to UTM Zone 13N (for Colorado)
gdf_utm = gdf.to_crs(epsg=32613)

# 5. Extract easting and northing
gdf_utm["easting"] = gdf_utm.geometry.x
gdf_utm["northing"] = gdf_utm.geometry.y

# 6. Save to CSV
gdf_utm.drop(columns="geometry").to_csv("output_with_utm.csv", index=False)

# 7. Print to verify
print(gdf_utm[["pointid", "easting", "northing"]])
