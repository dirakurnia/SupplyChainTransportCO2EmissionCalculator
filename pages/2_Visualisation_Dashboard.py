import pandas as pd
import streamlit as st
import networkx as nx
import osmnx as ox
import folium
import math
from streamlit_folium import st_folium


st.set_page_config(layout="wide")

st.title("Visualisation Page")

st.write("### Summary")
st.write(st.session_state.final_summary_data)

# -----------------For Calculating Distance between Airports or Harbour------------------------------
def distance_2_points(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Earth volumetric radius in kilometers (mean radius) based on NASA
    earth_radius = 6371.0
    distance = earth_radius * c
    return distance
# ---------------------------------------------------------------------------------------------------

# ----LONG RUNTIME, JUST AS REFERENCE----For Calculating Water and Land Best Route and It's Distance between Addresses--------
def route_distance_2_points(lat1, lon1, lat2, lon2, transport_type):

    landway_filter = {'highway': True}  # Filter for roads and paths (landways)
    waterway_filter = {'waterway': True}  # Filter for waterways (rivers, canals, etc.)

    if transport_type == "Land Freight" :
        G = ox.graph_from_point((lat1,lon1), dist=500*1000, custom_filter=landway_filter, simplify=True)
    else : # transport_type == "Water Freight" :
        G = ox.graph_from_point((lat1,lon1), dist=500*1000, custom_filter=waterway_filter, simplify=True)

    # Find nearest network nodes to start and end points
    orig_node = ox.distance.nearest_nodes(G, X=lon1, Y=lat1)
    dest_node = ox.distance.nearest_nodes(G, X=lon2, Y=lat2)

    # Compute path (Dijkstra's algorithm)
    route = nx.shortest_path(G, orig_node, dest_node, weight="length")

    # Calculate the total distance of the route in meters
    total_distance_meters = 0
    for u, v in zip(route[:-1], route[1:]):  # Iterating over each edge in the path
        total_distance_meters += G[u][v][0]['length']  # Getting the length of each edge

    # Convert distance from meters to kilometers
    total_distance_km = total_distance_meters / 1000

    # Convert route nodes to coordinates
    route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
    return total_distance_km, route_coords
# ---------------------------------------------------------------------------------------------------


emission_factor_data = pd.read_csv("Emission_Factor_Data.csv")
# ------------------------------For Calculating Emission / Tonne-------------------------------------
def emission_calculation_per_tonne(factor_data, transport_type, distance) :
    emission = factor_data.loc[factor_data["Transport Type"] == transport_type, "Emission Factor"] * distance
    return emission.values[0]
# ---------------------------------------------------------------------------------------------------

#------------------------------For Visualising Map---------------------------------------------------
def folium_map(data, distance_dict, factor_data) :
    # Create a base map centered around a specific location
    world_map = folium.Map(location=[20, 0], zoom_start=2)

    # Initialize map centered at the first location
    m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=2)

    # Iterate through each row and add a marker
    for index, row in data.iterrows():
        if row["Transport Type"] == "Water Freight" :
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Port Name"] + " Lat :" + str(row["Latitude"]) + "Lon :" + str(row["Longitude"]),  # Popup text on click
                tooltip=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Port Name"],  # Tooltip text on hover
                icon=folium.Icon(color="green", icon="ship")  # Custom icon
            ).add_to(m)

        elif row["Transport Type"] == "Air Freight" :
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Airport Name"] + " Lat :" + str(row["Latitude"]) + "Lon :" + str(row["Longitude"]),  # Popup text on click
                tooltip=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Airport Name"],
                # Tooltip text on hover
                icon=folium.Icon(color="red", icon="plane")  # Custom icon
            ).add_to(m)

        else : # row["Transport Type"] == "Land Freight"
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Address"] + " Lat :" + str(row["Latitude"]) + "Lon :" + str(row["Longitude"]),  # Popup text on click
                tooltip=row['Origin / Destination'] + " Trip " + str(row["Trip Number"]) + ": " + row["Country"] + ", " + row["Address"],
                # Tooltip text on hover
                icon=folium.Icon(color="gray", icon="map-marker")  # Custom icon
            ).add_to(m)

    for index in range(0, len(data),2) :
        row_origin = data.iloc[index]
        row_destination = data.iloc[index+1]

        if row_origin["Transport Type"] == "Water Freight":
            (folium.PolyLine(
                locations=[(row_origin["Latitude"], row_origin["Longitude"]), (row_destination["Latitude"], row_destination["Longitude"])],  # Connect each pair of consecutive points
                color="blue",
                weight=3,
                opacity=0.8
            ).add_child(
                folium.Tooltip(f"Trip {row_origin["Trip Number"]} Distance (km) : " + str(round(distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"], 2)))
            ).add_child(folium.Popup(str(emission_calculation_per_tonne(factor_data, "Water Freight", distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"]))+" \nkgCO2 / Tonne"))
             .add_to(m))

        elif row_origin["Transport Type"] == "Air Freight":
            (folium.PolyLine(
                locations=[(row_origin["Latitude"], row_origin["Longitude"]),
                           (row_destination["Latitude"], row_destination["Longitude"])],
                # Connect each pair of consecutive points
                color="red",
                weight=3,
                opacity=0.8
            ).add_child(
                folium.Tooltip(f"Trip {row_origin["Trip Number"]} Distance (km) : " + str(round(distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"], 2)))
            ).add_child(folium.Popup(str(emission_calculation_per_tonne(factor_data, "Air Freight", distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"]))+" \nkgCO2 / Tonne"))
             .add_to(m))

        else : # row_origin["Transport Type"] == "Land Freight":
            (folium.PolyLine(
                locations=[(row_origin["Latitude"], row_origin["Longitude"]),
                           (row_destination["Latitude"], row_destination["Longitude"])],
                # Connect each pair of consecutive points
                color="black",
                weight=3,
                opacity=0.8
            ).add_child(
                folium.Tooltip(f"Trip {row_origin["Trip Number"]} Distance (km) : " + str(round(distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"], 2)))
            ).add_child(folium.Popup(str(emission_calculation_per_tonne(factor_data, "Land Freight", distance_dict[f"Trip {row_origin["Trip Number"]} Distance (km)"]))+" \nkgCO2 / Tonne"))
             .add_to(m))

    # Show the map
    return m
#----------------------------------------------------------------------------------------------------




trips_distance_dict = {}
for trip in list(set(st.session_state.final_summary_data["Trip Number"])) :
    trip_data = st.session_state.final_summary_data.loc[st.session_state.final_summary_data["Trip Number"] == trip,:]
    lat1, lon1 = trip_data.loc[trip_data["Origin / Destination"] == "Origin", ["Latitude", "Longitude"]].iloc[0]
    lat2, lon2 = trip_data.loc[trip_data["Origin / Destination"] == "Destination", ["Latitude", "Longitude"]].iloc[0]
    trips_distance_dict[f"Trip {trip} Distance (km)"] = distance_2_points(lat1, lon1, lat2, lon2)

st.write("Calculation is based on Coordinate Distance")
st.write("*Unable to find Best-Route-Distance in short-time processing*")

st.write(trips_distance_dict)

st.write("#### To get Trip's kgCO2 emission per Tonne of Logistics, click the line :")

m = folium_map(st.session_state.final_summary_data, trips_distance_dict, emission_factor_data)
st_folium(m, width = 1000, height = 500)

colSlider, colGap = st.columns([6, 1])
with colSlider:
    tonne_logistics = st.slider("How many **Tonne** be brought in the Trip?", min_value = 0.0, max_value = 100.0, step = 0.1)

colWaterResult,colLandResult,colAirResult = st.columns(3)

with colWaterResult :
    st.write(":passenger_ship: Water Freight Emission:passenger_ship:")
    water_trip_numbers = st.session_state.final_summary_data.loc[
        st.session_state.final_summary_data["Transport Type"] == "Water Freight", "Trip Number"].values
    total_water_emission = 0
    for water_trip_number in water_trip_numbers :
        total_water_emission += tonne_logistics * emission_calculation_per_tonne(emission_factor_data, "Water Freight",
                                                               trips_distance_dict[f"Trip {water_trip_number} Distance (km)"])
    st.write(f"### {round(total_water_emission,2)} kgCO2")
with colLandResult :
    st.write(":pickup_truck: Land Freight Emission:pickup_truck:")
    land_trip_numbers = st.session_state.final_summary_data.loc[
        st.session_state.final_summary_data["Transport Type"] == "Land Freight", "Trip Number"].values
    total_land_emission = 0
    for land_trip_number in land_trip_numbers:
        total_land_emission += tonne_logistics * emission_calculation_per_tonne(emission_factor_data, "Land Freight",
                                                               trips_distance_dict[f"Trip {land_trip_number} Distance (km)"])
    st.write(f"### {round(total_land_emission,2)} kgCO2")
with colAirResult :
    st.write(":small_airplane: Air Freight Emission:small_airplane:")
    air_trip_numbers = st.session_state.final_summary_data.loc[
        st.session_state.final_summary_data["Transport Type"] == "Air Freight", "Trip Number"].values
    total_air_emission = 0
    for air_trip_number in air_trip_numbers:
        total_air_emission += tonne_logistics * emission_calculation_per_tonne(emission_factor_data, "Air Freight",
                                                              trips_distance_dict[f"Trip {air_trip_number} Distance (km)"])
    st.write(f"### {round(total_air_emission,2)} kgCO2")








