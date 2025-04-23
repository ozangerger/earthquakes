import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from geopy.distance import geodesic

cities = gpd.read_file('data/ne_110m_populated_places/ne_110m_populated_places.shp')
istanbul_coords = (41.0082, 28.9784)

def is_near_istanbul(city_geom):
    city_coords = (city_geom.y, city_geom.x)
    return geodesic(istanbul_coords, city_coords).km <= 250

near_istanbul = cities[cities['geometry'].apply(is_near_istanbul)]

df = pd.read_csv("data/son_depremler.csv")

plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax_offset = 0.8
ax.set_extent([df['Boylam(E)'].min() - ax_offset, df['Boylam(E)'].max() + ax_offset,
               df['Enlem(N)'].min() - ax_offset, df['Enlem(N)'].max() + ax_offset])

ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.gridlines(draw_labels=True)

for idx, row in near_istanbul.iterrows():
    city_point = row['geometry']
    ax.plot(city_point.x, city_point.y, marker='o', color='blue', markersize=5, transform=ccrs.PlateCarree())
    ax.text(city_point.x + 0.1, city_point.y, row['NAME'], fontsize=8, transform=ccrs.PlateCarree())

scatter = ax.scatter(
    df['Boylam(E)'], df['Enlem(N)'],
    c=df['ML'], s=df['ML'] * 10,
    cmap='Reds', edgecolor='black',
    transform=ccrs.PlateCarree()
)

plt.scatter(df['Boylam(E)'], df['Enlem(N)'], c=df['ML'], s=df['ML']*10, cmap='Reds', edgecolor='k')
plt.title("Earthquake Locations (ML shown by color and size)")
cbar = plt.colorbar(scatter, ax=ax, orientation='horizontal', shrink=0.6, pad=0.06)
cbar.set_label('Magnitude (ML)')
plt.savefig("last_earthquakes_istanbul.png", bbox_inches='tight', pad_inches=0.1)