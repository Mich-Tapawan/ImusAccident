import geopandas as gpd
import pandas as pd
import folium
from flask import render_template_string

def generate_heat_map(file_path):
    geojson_path = "./static/assets/Imus.geojson"
    barangay_map = gpd.read_file(geojson_path)

    df_2022 = pd.read_excel(file_path, sheet_name='brgy 2022', header=2)
    df_2023 = pd.read_excel(file_path, sheet_name='brgy 2023', header=2)
    df_2024 = pd.read_excel(file_path, sheet_name='brgy 2024', header=2)

    # Combine the datasets and drop 'Grand Total' rows
    df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)
    df = df[df['Barangay Name'] != 'Grand Total']

    # Clean and standardize the barangay names
    df['Barangay Name'] = df['Barangay Name'].str.strip().str.title()
    barangay_map['NAME_3'] = barangay_map['NAME_3'].str.strip().str.title()

    # Merge the traffic data with the barangay map
    barangay_map = barangay_map.merge(df, left_on="NAME_3", right_on="Barangay Name")

    # Create a map centered on Imus City
    m = folium.Map(location=[14.4296, 120.9367], zoom_start=13)

    # Add a Choropleth layer
    folium.Choropleth(
        geo_data=barangay_map,
        name="choropleth",
        data=barangay_map,
        columns=["Barangay Name", "Count of barangay"],
        key_on="feature.properties.NAME_3",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Traffic Incident Count"
    ).add_to(m)

    return m._repr_html_() 
