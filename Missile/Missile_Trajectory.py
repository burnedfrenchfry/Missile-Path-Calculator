import tkinter as tk
from tkinter import ttk
from geopy.geocoders import Nominatim
import folium
from geopy.exc import GeocoderTimedOut
import math
import webbrowser



#- Missile Specs (Weight in kg, thrust in kN, radius in meters)
missile_specs = {
    "LGM-30G Minuteman III ICBM": {"weight": 32158, "thrust": 935, "radius": 2500, "speed": 6705},
    "Trident II D5 Missile": {"weight": 58500, "thrust": 900, "radius": 8000, "speed": 6705}
}

#- Damage Areas
light_damage_zone = 50
moderate_damage_zone = 100
severe_damage_zone = 150

#- Military Bases w/ coordinates
base_coordinates = {
    "Malmstorm Air Force Base, Montana": (47.5082, -111.1914),
    "F.E. Warren Air Force Base, Wyoming": (41.1538, -104.8598),
    "Minot Air Force Base, North Dakota": (48.4157, -101.3579),
    "Nellis Air Force Base, Nevada": (36.2407, -115.0421),
    "Whiteman Air Force Base, Missouri": (38.7324, -93.5676),
    "Naval Base Kitsap, Washington": (47.5624, -122.6497)
}

# Initialize the global map_div variable once
map_div = folium.Map(location=[0, 0], zoom_start=2)


#- Blast Radius Calculation
def calculate_blast_radius():
    global map_div

    selected_missile = missile_var.get()
    destination_location = destination_entry.get()

    weight = missile_specs[selected_missile]["weight"]
    thrust = missile_specs[selected_missile]["thrust"]
    radius = missile_specs[selected_missile]["radius"]
    speed = missile_specs["speed"]

    #*************************
    geolocator = Nominatim(user_agent="geo_locator_app")
    try:
        location = geolocator.geocode(destination_location)
        destination_coordinates = (location.latitude, location.longitude)
    except (AttributeError, GeocoderTimedOut):
        result_label.config(text="Invalid destination location")
        return

    #- Calculate blast radius
    blast_radius = radius + (thrust / weight) * 1000 #Convert kN to N

    #- Damage Zones
    light_damage_zone_coords = get_circle_coordinates(destination_coordinates, light_damage_zone)
    moderate_damage_zone_coords = get_circle_coordinates(destination_coordinates, moderate_damage_zone)
    severe_damage_zone_coords = get_circle_coordinates(destination_coordinates, severe_damage_zone)

    # Add circles for damage zones to the map_div
    folium.Circle(location=light_damage_zone_coords, radius=light_damage_zone, color='lightcoral',
                  fill=True, fill_opacity=0.3).add_to(map_div)
    folium.Circle(location=moderate_damage_zone_coords, radius=moderate_damage_zone, color='indianred',
                  fill=True, fill_opacity=0.5).add_to(map_div)
    folium.Circle(location=severe_damage_zone_coords, radius=severe_damage_zone, color='darkred',
                  fill=True, fill_opacity=0.7).add_to(map_div)

    # Save the map to an HTML file
    map_div.save('missile_path.html')

    webbrowser.open('missile_path.html')

    # Update the result label
    result_label.config(text=f"Blast Radius: {blast_radius:.2f} meters\n"
                             f"Light Damage Zone: {light_damage_zone} meters\n"
                             f"Moderate Damage Zone: {moderate_damage_zone} meters\n"
                             f"Severe Damage Zone: {severe_damage_zone} meters\n"
                             f"Map created. Open missile_path.html to view.")

#- Function to calculate coordinates of a circle
def get_circle_coordinates(center, radius):
    lat, lon = center
    lat_change = radius / 111.32
    lon_change = radius / (40075 * math.cos(math.radians(lat)) / 360)
    return [
        (lat + lat_change, lon),
        (lat - lat_change, lon),
        (lat, lon + lon_change),
        (lat, lon - lon_change)
    ]


def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    # Radius of the Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    # Convert distance from meters to miles
    distance_miles = distance * 0.000621371

    return distance_miles


# Function to handle button click event
def show_map():
    global map_div

    selected_base = base_var.get()
    destination_location = destination_entry.get()

    # Get coordinates for destination using Nominatim geocoder
    geolocator = Nominatim(user_agent="geo_locator_app")
    try:
        location = geolocator.geocode(destination_location)
        destination_coordinates = (location.latitude, location.longitude)
    except (AttributeError, GeocoderTimedOut):
        result_label.config(text="Invalid destination location")
        return

     # Calculate distance between base and destination in miles
    distance_miles = calculate_distance(base_coordinates[selected_base], destination_coordinates)

    # Create a new map centered at the average coordinates of the base and destination
    map_center = [(base_coordinates[selected_base][0] + destination_coordinates[0]) / 2,
                  (base_coordinates[selected_base][1] + destination_coordinates[1]) / 2]
    map_div = folium.Map(location=map_center, zoom_start=5)

    # Calculate distance between base and destination
    distance = calculate_distance(base_coordinates[selected_base], destination_coordinates)

    # Calculate time to arrival using missile speed
    selected_missile = missile_var.get()
    missile_speed = missile_specs[selected_missile]["speed"]
    time_to_arrival = distance / missile_speed  # Time in seconds

    # Calculate time to arrival using missile speed in meters per second
    time_to_arrival = distance_miles * 1609.34 / missile_speed  # Convert miles to meters


    # Convert time to arrival from seconds to minutes
    time_to_arrival_minutes = time_to_arrival / 60

    # Create a new map centered at the average coordinates of the base and destination
    map_center = [(base_coordinates[selected_base][0] + destination_coordinates[0]) / 2,
                  (base_coordinates[selected_base][1] + destination_coordinates[1]) / 2]

    # Create a new map
    map_div = folium.Map(location=map_center, zoom_start=5)

    # Display the map with markers for base and destination
    folium.Marker(location=base_coordinates[selected_base], popup='Base').add_to(map_div)
    folium.Marker(location=destination_coordinates, popup='Destination').add_to(map_div)
    folium.PolyLine([base_coordinates[selected_base], destination_coordinates], color="blue",
                    weight=2.5, opacity=1).add_to(map_div)


    # Add distance and time to arrival information in the HTML popup
    popup_html = f"<b>Distance:</b> {distance_miles:.2f} miles<br><b>Time to Arrival:</b> {time_to_arrival_minutes:.2f} minutes (~{time_to_arrival_minutes:.2f} minutes)"
    folium.Popup(popup_html).add_to(folium.Marker(location=destination_coordinates, popup=popup_html))


    print("Base Coordinates:", base_coordinates[selected_base])
    print("Destination Coordinates:", destination_coordinates)
    print("Distance (Miles):", distance)
    print("Time to Arrival (Minutes):", time_to_arrival_minutes)

    # Save the map to an HTML file
    map_div.save('missile_path.html')
    # Open the HTML file in the default web browser
    webbrowser.open('missile_path.html')

    # Update the result label
    result_label.config(text=f"Map created. Open missile_path.html to view.")



# Create Tkinter GUI
root = tk.Tk()
root.title("Missile Path Calculator")

# Drop Down For Selecting Missile
missile_var = tk.StringVar()
missile_label = tk.Label(root, text="Select a missile:")
missile_label.pack()

missile_dropdown = ttk.Combobox(root, textvariable=missile_var, values=list(missile_specs.keys()))
missile_dropdown.pack()



# Dropdown for selecting base**********************
base_var = tk.StringVar()
base_label = tk.Label(root, text="Select a military or naval base:")
base_label.pack()

base_dropdown = ttk.Combobox(root, textvariable=base_var, values=list(base_coordinates.keys()))
base_dropdown.pack()
#*************************


# Entry for entering destination
destination_label = tk.Label(root, text="Enter destination location:")
destination_label.pack()

destination_entry = tk.Entry(root)
destination_entry.pack()

# Button to calculate and display the map
calculate_button = tk.Button(root, text="Calculate Blast Radius and Show Map", command=show_map)
calculate_button.pack()

# Label for displaying the result
result_label = tk.Label(root, text="")
result_label.pack()

# Folium map
#map_div = folium.Map(location=[0, 0], zoom_start=2)

# Start the Tkinter main loop
root.mainloop()
