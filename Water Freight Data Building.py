import pandas as pd
import requests
from deep_translator import GoogleTranslator
import warnings

warnings.filterwarnings("ignore")


class WaterFreightDataBuilding:
    # Initialise a class with reading the data
    def __init__(self):
        self.existing_data = pd.read_csv("Water_Freight_Data.csv")
        return
    def get_harbour_lat_lon(self):
        # Overpass API URL
        overpass_url = "https://overpass-api.de/api/interpreter"

        # Overpass Query to Get All Ports
        query = """
        [out:json];
        node["harbour"];
        out;
        """

        # Make Request
        response = requests.get(overpass_url, params={'data': query}).json()

        # Extract and Print Port Names with Coordinates
        ports_data = pd.DataFrame(columns=["Port Name", "Latitude", "Longitude"])
        for element in response["elements"]:
            try:
                new_row = {"Port Name": element["tags"]["name"], "Latitude": element["lat"],
                           "Longitude": element["lon"]}
                # Append the row using loc
                ports_data.loc[len(ports_data)] = new_row
            except:
                continue
        return ports_data

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
    def get_harbour_country(self, ports_data):
        list_country = []
        # Fill in the list
        for i in range(len(ports_data)):
            print(i, "out of ", len(ports_data), ports_data.iloc[i, 0])
            country = self.get_country(ports_data.iloc[i, 1], ports_data.iloc[i, 2])
            print("--The Country is {}".format(country))
            list_country.append(country)
        # Append the list to Data Frame as new column
        ports_data["Country Raw"] = list_country

        # Translated and Stripped
        country_column_distinct_values = list(set(list_country))
        translator = GoogleTranslator(source='auto', target='en')
        translated_dict = {country: translator.translate(country).split("/")[0].strip().title() for country in
                           country_column_distinct_values}
        translated_dict["España"] = "Spain"
        ports_data["Country"] = ports_data.apply(lambda row : translated_dict[row["Country Raw"]], axis = 1)
        return ports_data

    def update_water_freight_data(self):
        generated_data = self.get_harbour_lat_lon()
        existing_ports = list(self.existing_data["Port Name"].values)
        generated_ports = list(generated_data["Port Name"].values)
        new_ports = [item for item in generated_ports if item not in existing_ports]
        print(new_ports)
        if new_ports != [] :
            sliced_generated_data = generated_data.loc[generated_data["Port Name"].isin(new_ports), :]
            sliced_generated_data = self.get_harbour_country(sliced_generated_data)
            updated_data = pd.concat([self.existing_data, sliced_generated_data]).reset_index().drop(
                ["index"], axis=1)

            updated_data.to_csv("Water_Freight_Data.csv", index=False)
            print(f"Previous Records : {len(updated_data)}")
            print(f"New Records : {len(self.existing_data)}")
        else :
            print(f"Previous Records : {len(self.existing_data)}")
            print(f"New Records : {len(self.existing_data)}")
            print("No Change")

        return

updateWaterFreightData = WaterFreightDataBuilding()
updateWaterFreightData.update_water_freight_data()