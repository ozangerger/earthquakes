import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil

url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

pre_tag = soup.find("pre")
if not pre_tag:
    print("Error: No <pre> tag found on the page.")
    exit()

lines = pre_tag.get_text().splitlines()[6:]
records = []

for line in lines:
    parts = line.split()
    if len(parts) < 7:
        continue

    date, time, lat, lon, depth = parts[0], parts[1], parts[2], parts[3], parts[4]
    location_str = " ".join(parts[6:])
    
    if "MARMARA DENIZI" in location_str.upper():
        try:
            magnitude = float(parts[6])
        except ValueError:
            continue

        cleaned_location = " ".join(parts[8:]) if len(parts) > 8 else "MARMARA DENIZI"
        records.append([date, time, lat, lon, depth, magnitude, cleaned_location])

df = pd.DataFrame(records, columns=["Date", "Time", "Latitude", "Longitude", "Depth(km)", "Magnitude", "Location"])
file = "data/marmara_earthquakes.csv"
if(os.path.exists(file)):
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    new_file = f"data/archive/marmara_earthquakes_{timestamp}.csv"
    shutil.copyfile(file, new_file)
df.to_csv(file, index=False)

print(f"Saved {len(df)} list of earthquakes to 'data/marmara_earthquakes.csv'")
