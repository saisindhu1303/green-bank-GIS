import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

# === Load the Excel file ===
df = pd.read_excel("green_innovation_banks.xlsx")

# === Optional: Clean messy addresses ===
df["CleanedAddress"] = df["Address"].str.split("/").str[0].str.strip()

# === Predefined coordinates for some known banks ===
predefined_coords = {
    "Connecticut Green Bank": (41.7637, -72.6851),
    "New York Green Bank": (40.7537, -73.9934),
    "DC Green Bank": (38.9039, -77.0422),
    "Hawaii Green Infrastructure Authority": (21.3069, -157.8583),
    "Michigan Saves": (42.7336, -84.5555),
    "Montgomery County Green Bank": (39.0839974, -77.1527574),
    "Rhode Island Infrastructure Bank": (41.8239891, -71.4128343),
    "California I-Bank (CLEEN Center)": (38.578001, -121.489133),
    "Solar and Energy Loan Fund (SELF)": (29.177480, -81.008820),
    "Clean Energy Credit Union": (40.0150, -105.2705),  # Boulder, CO
    "Greenpenny": (43.3033, -91.7854),  # Decorah, IA
    "Nevada Clean Energy Fund": (39.1638, -119.7674),  # Carson City
}

# === Assign predefined coordinates ===
df["Latitude"] = df["Name"].apply(lambda name: predefined_coords.get(name, (None, None))[0])
df["Longitude"] = df["Name"].apply(lambda name: predefined_coords.get(name, (None, None))[1])

# === Use geopy for banks with missing coordinates ===
geolocator = Nominatim(user_agent="green_bank_locator")

def geocode_if_missing(row):
    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
        return row["Latitude"], row["Longitude"]
    try:
        location = geolocator.geocode(row["CleanedAddress"])
        sleep(1)  # Be kind to the API
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding failed for: {row['Name']}, reason: {e}")
    return None, None

# Apply geocoding only where needed
df[["Latitude", "Longitude"]] = df.apply(
    lambda row: pd.Series(geocode_if_missing(row)), axis=1
)

# === Save updated file ===
df.to_excel("green_innovation_banks_with_coords.xlsx", index=False)

print("✅ Coordinates added and file saved as 'green_innovation_banks_with_coords.xlsx'")
