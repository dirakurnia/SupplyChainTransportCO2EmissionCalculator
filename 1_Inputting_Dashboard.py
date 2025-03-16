import streamlit as st
import pandas as pd
import requests

if "final_summary_data" not in st.session_state :
    st.session_state.final_summary_data = pd.DataFrame()

st.set_page_config(layout="wide")

st.title("Welcome to Inputting Data Page")

st.write("### Input your Logistic Transport Origin-Destination")
st.write("Choose Your Transportation Type")

ports_data = pd.read_csv("Water_Freight_Data.csv")
airports_data = pd.read_csv("Air_Freight_Data.csv")

#-------------For Search Address------------------------------------
def search_address(query):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=5"
    headers = {"User-Agent": "MyApp"}  # Required to avoid being blocked
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        results = response.json()
        return [{"address": place["display_name"], "lat": place["lat"], "lon": place["lon"]} for place in results]
    else:
        return []
#-------------------------------------------------------------------

#-------------For Unpack Latitude and Longitude------------------------------------
def unpack_lat_lon(data, transport_type, port_or_airport_or_address_name):
    if transport_type == "Water Freight" :
        lat = float(data.loc[data["Port Name"] == port_or_airport_or_address_name, "Latitude"])
        lon = float(data.loc[data["Port Name"] == port_or_airport_or_address_name, "Longitude"])
        return [lat,lon]
    elif transport_type == "Air Freight":
        lat = float(data.loc[data["Airport Name"] == port_or_airport_or_address_name, "Latitude"])
        lon = float(data.loc[data["Airport Name"] == port_or_airport_or_address_name, "Longitude"])
        return [lat,lon]
    else : # Land Freight
        lat = float(search_address(port_or_airport_or_address_name)[0]["lat"])
        lon = float(search_address(port_or_airport_or_address_name)[0]["lon"])
        return [lat,lon]
#-----------------------------------------------------------------------------------

colWater, colLand, colAir = st.columns(3)

with colWater:
    if "show_content_water_input" not in st.session_state:
        st.session_state.show_content_water_input = False  # Initialize to False (hidden)

    if st.button(":passenger_ship: Water Freight Origin", key="water") :
        st.session_state.show_content_water_input = not st.session_state.show_content_water_input


    if st.session_state.show_content_water_input :
        ports_countries = list(set(ports_data["Country"]))
        selected_country_port = st.selectbox("Select a Country of Origin:", ports_countries, key="water_origin_country")

        if selected_country_port :
            ports_in_selected_country = list(set(ports_data.loc[ports_data["Country"] == selected_country_port, "Port Name"]))
            selected_port = st.selectbox(f"Choose a port in {selected_country_port} :", ports_in_selected_country, key="water_origin_port")

            if selected_port :
                st.write(f"You have selected an Origin Port : **{selected_country_port}, {selected_port}**")


    if "show_content_water_input_2" not in st.session_state:
        st.session_state.show_content_water_input_2 = False  # Initialize to False (hidden)

    if st.button("Water Freight Destination :passenger_ship:", key="water_destination") :
        st.session_state.show_content_water_input_2 = not st.session_state.show_content_water_input_2

    if st.session_state.show_content_water_input_2 :
        ports_countries_2 = list(set(ports_data["Country"]))
        selected_country_port_2 = st.selectbox("Select a Country of Destination:", ports_countries_2, key="water_destination_country")

        if selected_country_port_2:
            ports_in_selected_country_2 = list(
                set(ports_data.loc[ports_data["Country"] == selected_country_port_2, "Port Name"]))
            selected_port_2 = st.selectbox(f"Choose a port in {selected_country_port_2} :", ports_in_selected_country_2, key="water_destination_port")

            if selected_port_2:
                st.write(f"You have selected a Destination Port : **{selected_country_port_2}, {selected_port_2}**")

with colLand:
    if "show_content_land_input" not in st.session_state:
        st.session_state.show_content_land_input = False  # Initialize to False (hidden)

    if st.button(":pickup_truck: Land Freight Origin", key="land") :
        st.session_state.show_content_land_input = not st.session_state.show_content_land_input

    if st.session_state.show_content_land_input :
        user_input = st.text_input("Enter (any) Address of Origin:", key = "user_input_land_origin")
        if user_input:
            search_results = search_address(user_input)
            addresses = [result["address"] for result in search_results]

            if addresses:
                selected_address = st.selectbox("Select an Address :", addresses, key = "land_origin_address")
                if selected_address:
                    st.write(f"You selected origin address: {selected_address}")

            else:
                st.write("No matching results found.")

    if "show_content_land_input_2" not in st.session_state:
        st.session_state.show_content_land_input_2 = False  # Initialize to False (hidden)

    if st.button("Land Freight Destination :pickup_truck:", key="land_destination") :
        st.session_state.show_content_land_input_2 = not st.session_state.show_content_land_input_2

    if st.session_state.show_content_land_input_2 :
        user_input_2 = st.text_input("Enter (any) Address of Destination:", key = "user_input_land_destination")
        if user_input_2:
            search_results_2 = search_address(user_input_2)
            addresses_2 = [result["address"] for result in search_results_2]

            if addresses_2:
                selected_address_2 = st.selectbox("Select an Address :", addresses_2, key = "land_destination_address")
                if selected_address_2:
                    st.write(f"You selected destination address: {selected_address_2}")

            else:
                st.write("No matching results found.")

with colAir:
    if "show_content_air_input" not in st.session_state:
        st.session_state.show_content_air_input = False  # Initialize to False (hidden)

    if st.button(":small_airplane: Air Freight Origin", key="air"):
        st.session_state.show_content_air_input = not st.session_state.show_content_air_input

    if st.session_state.show_content_air_input:
        airports_countries = list(set(airports_data["Country"]))
        selected_country_airport = st.selectbox("Select a Country of Origin:", airports_countries, key="air_origin_country")
        if selected_country_airport :
            airports_in_selected_country = list(set(airports_data.loc[airports_data["Country"] == selected_country_airport, "Airport Name"]))
            selected_airport = st.selectbox(f"Choose an airport in {selected_country_airport} :", airports_in_selected_country, key="air_origin_airport")

            if selected_airport :
                st.write(f"You have selected origin airport  : **{selected_country_airport}, {selected_airport}**")


    if "show_content_air_input_2" not in st.session_state:
        st.session_state.show_content_air_input_2 = False  # Initialize to False (hidden)

    if st.button("Air Freight Destination :small_airplane:", key="air_destination"):
        st.session_state.show_content_air_input_2 = not st.session_state.show_content_air_input_2

    if st.session_state.show_content_air_input_2:
        airports_countries_2 = list(set(airports_data["Country"]))
        selected_country_airport_2 = st.selectbox("Select a Country of Destination:", airports_countries_2, key="air_destination_country")
        if selected_country_airport_2 :
            airports_in_selected_country_2 = list(set(airports_data.loc[airports_data["Country"] == selected_country_airport_2, "Airport Name"]))
            selected_airport_2 = st.selectbox(f"Choose an airport in {selected_country_airport_2} :", airports_in_selected_country_2)

            if selected_airport_2 :
                st.write(f"You have selected a destination airport : **{selected_country_airport_2}, {selected_airport_2}**")

st.divider()  # Adds a horizontal line

st.write("### Review")

colReviewButton, colReview = st.columns([1, 4])

if "show_content_water_review" not in st.session_state:
    st.session_state.show_content_water_review = False  # Initialize to False (hidden)
if "show_content_land_review" not in st.session_state:
    st.session_state.show_content_land_review = False  # Initialize to False (hidden)
if "show_content_air_review" not in st.session_state:
    st.session_state.show_content_air_review = False  # Initialize to False (hidden)

with colReviewButton :
    if st.session_state.show_content_water_input and st.session_state.show_content_water_input_2 :
        if st.button(":passenger_ship: Water Freight Review :passenger_ship:") :
            st.session_state.show_content_water_review = not st.session_state.show_content_water_review
            st.session_state.show_content_land_review = False
            st.session_state.show_content_air_review = False
    if st.session_state.show_content_land_input and st.session_state.show_content_land_input_2:
        if st.button(":pickup_truck: Land Freight Review :pickup_truck:") :
            st.session_state.show_content_water_review = False
            st.session_state.show_content_land_review = not st.session_state.show_content_land_review
            st.session_state.show_content_air_review = False
    if st.session_state.show_content_air_input and st.session_state.show_content_air_input_2:
        if st.button(":small_airplane: Air Freight Review :small_airplane:") :
            st.session_state.show_content_water_review = False
            st.session_state.show_content_land_review = False
            st.session_state.show_content_air_review = not st.session_state.show_content_air_review

with colReview :
    if st.session_state.show_content_water_review and st.session_state.show_content_water_input and st.session_state.show_content_water_input_2:
        [lat1, lon1] = unpack_lat_lon(ports_data, "Water Freight", selected_port)
        [lat2, lon2] = unpack_lat_lon(ports_data, "Water Freight", selected_port_2)

        review_table = pd.DataFrame({
            "Transport Type": ["Water Freight", "Water Freight"],
            "Origin / Destination": ["Origin", "Destination"],
            "Country": [selected_country_port, selected_country_port_2],
            "Port Name": [selected_port, selected_port_2],
            "Latitude": [lat1, lat2],
            "Longitude": [lon1, lon2]
        })

        st.write(review_table)
        if "trip_number" not in st.session_state:
            st.session_state.trip_number = 1  # Initialize to 1 (first trip)
        if st.button(f"Assess as Trip {st.session_state.trip_number}") :
            review_table["Trip Number"] = st.session_state.trip_number
            st.session_state.final_summary_data = pd.concat([st.session_state.final_summary_data,review_table], ignore_index=True)
            st.session_state.trip_number += 1
        st.write("**After you click the 'Assess' Button, the Trip Number may not change straight away**")
        st.write("**No need to worry, just focus on input another Logistic Transport Origin-Destination then click the review**")
        st.write("**It should change after you click another review**")


    if st.session_state.show_content_land_review and st.session_state.show_content_land_input and st.session_state.show_content_land_input_2:
        [lat1, lon1] = unpack_lat_lon(ports_data, "Land Freight", selected_address)
        [lat2, lon2] = unpack_lat_lon(ports_data, "Land Freight", selected_address_2)

        review_table = pd.DataFrame({
            "Transport Type": ["Land Freight", "Land Freight"],
            "Origin / Destination": ["Origin", "Destination"],
            "Country": [selected_address.strip().split(", ")[-1], selected_address_2.strip().split(", ")[-1]],
            "Address": [selected_address, selected_address_2],
            "Latitude": [lat1, lat2],
            "Longitude": [lon1, lon2]
        })

        st.write(review_table)
        if "trip_number" not in st.session_state:
            st.session_state.trip_number = 1  # Initialize to 1 (first trip)
        if st.button(f"Assess as Trip {st.session_state.trip_number}") :
            review_table["Trip Number"] = st.session_state.trip_number
            st.session_state.final_summary_data = pd.concat([st.session_state.final_summary_data,review_table], ignore_index=True)
            st.session_state.trip_number += 1
        st.write("**After you click the 'Assess' Button, the Trip Number may not change straight away**")
        st.write("**No need to worry, just focus on input another Logistic Transport Origin-Destination then click the review**")
        st.write("**It should change after you click another review**")


    if st.session_state.show_content_air_review and st.session_state.show_content_air_input and st.session_state.show_content_air_input_2:
        [lat1, lon1] = unpack_lat_lon(airports_data, "Air Freight", selected_airport)
        [lat2, lon2] = unpack_lat_lon(airports_data, "Air Freight", selected_airport_2)

        review_table = pd.DataFrame({
            "Transport Type": ["Air Freight", "Air Freight"],
            "Origin / Destination": ["Origin", "Destination"],
            "Country": [selected_country_airport, selected_country_airport_2],
            "Airport Name": [selected_airport, selected_airport_2],
            "Latitude": [lat1, lat2],
            "Longitude": [lon1, lon2]
        })

        st.write(review_table)
        if "trip_number" not in st.session_state:
            st.session_state.trip_number = 1  # Initialize to 1 (first trip)
        if st.button(f"Assess as Trip {st.session_state.trip_number}") :
            review_table["Trip Number"] = st.session_state.trip_number
            st.session_state.final_summary_data = pd.concat([st.session_state.final_summary_data,review_table], ignore_index=True)
            st.session_state.trip_number += 1
        st.write("**After you click the 'Assess' Button, the Trip Number may not change straight away**")
        st.write("**No need to worry, just focus on input another Logistic Transport Origin-Destination then click the review**")
        st.write("**It should change after you click another review**")

st.divider()

st.write("### Summary")
st.write(st.session_state.final_summary_data)
st.write("if you made a mistake, you can go to triple vertical dot at the far upper-right, then click clear cache, then re-run")








