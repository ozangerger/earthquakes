import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from geopy.distance import geodesic

def readFaultData():
    geoJsonFiles = [
        "data/tekirdag_segmenti.geojson",
        "data/orta_marmara_cukuru.geojson",
        "data/kumburgaz_segmenti.geojson",
        "data/avcilar_segmenti.geojson",
        "data/cinarcik_segmenti.geojson"
    ]

    return gpd.GeoDataFrame(pd.concat([gpd.read_file(f) for f in geoJsonFiles], ignore_index=True))


def plotData(df, near_istanbul=None, min_magnitude=3.0, ax_offset = 0.8, fileName="last_earthquakes_istanbul.png"):
    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.set_extent([df['Longitude'].min() - ax_offset, df['Longitude'].max() + ax_offset,
                   df['Latitude'].min() - ax_offset, df['Latitude'].max() + ax_offset])

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)
    ax.gridlines(draw_labels=True)

    if(near_istanbul is not None):
        for idx, row in near_istanbul.iterrows():
            city_point = row['geometry']
            ax.plot(city_point.x, city_point.y, marker='o', color='blue', markersize=5, transform=ccrs.PlateCarree())
            ax.text(city_point.x + 0.1, city_point.y, row['NAME'], fontsize=8, transform=ccrs.PlateCarree())

    df = df[df['Magnitude'] >= min_magnitude]

    scatter = ax.scatter(
        df['Longitude'], df['Latitude'],
        c=df['Magnitude'], s=df['Magnitude'] * 3,
        cmap='Reds', edgecolor='black',
        transform=ccrs.PlateCarree()
    )

    faults = readFaultData()
    faults.plot(ax=ax, color='red', linewidth=1.5, alpha=0.6, transform=ccrs.PlateCarree())

    plt.title(f"Earthquake Locations (ML > {min_magnitude})")
    cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal', shrink=0.6, pad=0.06)
    cbar.set_label('Magnitude (ML)')
    plt.savefig(fileName, dpi=600, bbox_inches='tight', pad_inches=0.1)


def findNearestCities():
    cities = gpd.read_file('data/ne_110m_populated_places/ne_110m_populated_places.shp')
    istanbul_coords = (41.0082, 28.9784)

    def is_near_istanbul(city_geom):
        city_coords = (city_geom.y, city_geom.x)
        return geodesic(istanbul_coords, city_coords).km <= 250

    return cities[cities['geometry'].apply(is_near_istanbul)]


if __name__ == "__main__":
    near_istanbul = findNearestCities()
    df = pd.read_csv("data/marmara_earthquakes.csv")

    plotData(df, min_magnitude=3.0, near_istanbul=near_istanbul)
    plotData(df, min_magnitude=2.0, near_istanbul=None, ax_offset=0.1, fileName="last_earthquakes_istanbul_zoomed.png")