import pandas as pd
import requests
from deep_translator import GoogleTranslator
import warnings

warnings.filterwarnings("ignore")

class AirFreightDataBuilding:
    # Initialise a class with reading the data
    def __init__(self):
        self.existing_data = pd.read_csv("Air_Freight_Data.csv")
        return
    def get_airports_lat_lon(self):
        # Overpass API URL
        overpass_url = "https://overpass-api.de/api/interpreter"

        # Overpass Query to Get All Airports
        query = """
        [out:json];
        node["aeroway"="aerodrome"];
        out;
        """

        # Make Request
        response = requests.get(overpass_url, params={'data': query}).json()

        # Extract and Print Airport Names with Coordinates. ONLY EXTRACT AIRPORTS NAME THAT WITH ENGLISH LANGUAGE
        airport_data = pd.DataFrame(columns=["Airport Name", "Latitude", "Longitude"])
        for element in response["elements"]:
            try:
                new_row = {"Airport Name": element["tags"]["name:en"], "Latitude": element["lat"],
                           "Longitude": element["lon"]}
                airport_data.loc[len(airport_data)] = new_row
            except:
                continue
        return airport_data

    def get_country(self, lat, lon):
        # Use Open Source to get Country based on Latitude and Longitude
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "Mozilla/5.0"}  # Required to avoid blocking
        response = requests.get(nominatim_url, headers=headers)

        if response.status_code == 200:
            geo_data = response.json()
            return geo_data.get("address", {}).get("country", "Unknown")
        return "Unknown"

    # Run the function below for new rows with existing data to compare with
    def get_airports_country(self, airport_data):
        list_country = []
        # Fill in the list
        for i in range(len(airport_data)):
            print(i, "out of ", len(airport_data), airport_data.iloc[i, 0])
            country = self.get_country(airport_data.iloc[i, 1], airport_data.iloc[i, 2])
            print("--The Country is {}".format(country))
            list_country.append(country)
        # Append the list to Data Frame as new column
        airport_data["Country Raw"] = list_country

        # Translated and Stripped
        country_column_distinct_values = list(set(list_country))
        translator = GoogleTranslator(source='auto', target='en')
        translated_dict = {country: translator.translate(country).split("/")[0].strip().title() for country in
                           country_column_distinct_values}
        translated_dict["España"] = "Spain"
        airport_data["Country"] = airport_data.apply(lambda row : translated_dict[row["Country Raw"]], axis = 1)
        return airport_data

    def update_air_freight_data(self):
        generated_data = self.get_airports_lat_lon()
        existing_airports = list(self.existing_data["Airport Name"].values)
        generated_airports = list(generated_data["Airport Name"].values)
        new_airports = [item for item in generated_airports if item not in existing_airports]
        print(new_airports)
        if new_airports != [] :
            sliced_generated_data = generated_data.loc[generated_data["Airport Name"].isin(new_airports),:]
            sliced_generated_data = self.get_airports_country(sliced_generated_data)
            updated_data = pd.concat([self.existing_data, sliced_generated_data]).reset_index().drop(["index"], axis = 1)

            updated_data.to_csv("Air_Freight_Data.csv", index=False)
        else :
            print(f"Previous Records : {len(self.existing_data)}")
            print(f"New Records : {len(self.existing_data)}")
            print("No Change")

        return

updateAirFreightData = AirFreightDataBuilding()
updateAirFreightData.update_air_freight_data()


