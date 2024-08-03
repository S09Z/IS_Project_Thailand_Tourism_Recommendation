from taipy.gui import Gui
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load data (simulate the notebook's data loading steps)
def load_data():
    # Example DataFrame
    data = {
        'Province': ['Bangkok', 'Chiang Mai', 'Phuket'],
        'Latitude': [13.7563, 18.7883, 7.8804],
        'Longitude': [100.5018, 98.9853, 98.3883]
    }
    return pd.DataFrame(data)

# Load GeoJSON data for visualization
def load_geojson():
    geojson_file = 'hook/data/thai_province_coordinates_geo.json'
    gdf = gpd.read_file(geojson_file)
    return gdf

# Plot the geospatial data
def plot_geospatial_data():
    gdf = load_geojson()
    fig, ax = plt.subplots(figsize=(12, 8))
    gdf.plot(ax=ax, color='lightblue', edgecolor='black')
    bangkok = gdf[gdf['name'] == 'Bangkok Metropolis']
    if not bangkok.empty:
        bangkok.plot(ax=ax, color='red', edgecolor='black')
    ax.set_aspect('equal')
    ax.set_title('Map of Thai Provinces with Bangkok Highlighted', fontsize=15)
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    return fig

# GUI Content
def display_data():
    df = load_data()
    return df

# GUI Layout
layout = """
# Thai Tourism GUI

## Geospatial Map

<|{plot_geospatial_data}|plot|height=500px|>

## Data Table

<|{display_data}|table|>
"""

# Initialize and run the GUI
page = {
    "plot_geospatial_data": plot_geospatial_data,
    "display_data": display_data
}

gui = Gui(page)
gui.run()
