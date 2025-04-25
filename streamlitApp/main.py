import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm

def setFilters():
    st.sidebar.title("Filters")
    min_magnitude = st.sidebar.slider("Minimum Magnitude", 0.0, 10.0, 3.0, 0.1)
    return min_magnitude

def readFaultData():
    geoJsonFiles = [
        "../data/tekirdag_segmenti.geojson",
        "../data/orta_marmara_cukuru.geojson",
        "../data/kumburgaz_segmenti.geojson",
        "../data/avcilar_segmenti.geojson",
        "../data/cinarcik_segmenti.geojson"
    ]

    return gpd.GeoDataFrame(pd.concat([gpd.read_file(f) for f in geoJsonFiles], ignore_index=True))

def createMap(min_mag=3.0):
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
    df = pd.read_csv("../data/marmara_earthquakes.csv")
    colormap = cm.linear.viridis.scale(df["Magnitude"].min(), df["Magnitude"].max())
    colormap.label = 'Magnitude (ML)'
    df = df[df['Magnitude'] >= min_mag]

    if df is not df.empty:
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Magnitude'],
                color=colormap(row["Magnitude"]),
                fill=True,
                fill_opacity=0.6,
                popup=f"M {row['Magnitude']}"
            ).add_to(m)

        colormap.add_to(m)

    faults = readFaultData()
    folium.GeoJson(faults, name="Fault Lines", style_function=lambda x: {
        'color': 'red', 'weight': 2, 'opacity': 0.6
    }).add_to(m)

    folium.LayerControl().add_to(m)
    return m

if __name__ == "__main__":
    min_mag = setFilters()

    if "map_center" not in st.session_state:
        st.session_state.map_center = [40.9, 28.7]
    if "map_zoom" not in st.session_state:
        st.session_state.map_zoom = 7

    m = createMap(min_mag)
    st.title("Istanbul Earthquakes & Faults")
    st.markdown(f"### Showing earthquakes with magnitude ≥ {min_mag}")
    map_data = st_folium(m, width=600, height=600)

    new_center = map_data.get("center")
    new_zoom = map_data.get("zoom")

    if new_center and [new_center["lat"], new_center["lng"]] != st.session_state.map_center:
        st.session_state.map_center = [new_center["lat"], new_center["lng"]]

    if new_zoom and new_zoom != st.session_state.map_zoom:
        st.session_state.map_zoom = new_zoom