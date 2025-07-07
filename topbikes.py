import requests
import math
import folium
import webbrowser


def get_user_coordinates():
    try:
        latitude = float(input("Enter your latitude: "))
        longitude = float(input("Enter your longitude: "))
        return latitude, longitude
    except ValueError:
        print("Invalid input. Please enter numeric values for coordinates.")
        return None


def fetch_bike_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching bike data: {e}")
        return None


def fetch_station_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching station data: {e}")
        return None


def get_station_name(station_id, stations_data):
    if (
        not stations_data
        or "data" not in stations_data
        or "stations" not in stations_data["data"]
    ):
        return None

    for station in stations_data["data"]["stations"]:
        if station["station_id"] == station_id:
            return station.get("name", "Unknown Station")
    return "Unknown Station"


def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two coordinates
    R = 6371e3  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_closest_bikes(user_coords, bikes_data):
    if not user_coords or not bikes_data:
        return []

    latitude, longitude = user_coords
    valid_bikes = [
        {
            "bike_id": bike["bike_id"],
            "latitude": bike["lat"],
            "longitude": bike["lon"],
            "station_id": bike["station_id"],
            "current_range_meter": bike["current_range_meters"],
            "distance": calculate_distance(
                latitude, longitude, bike["lat"], bike["lon"]
            ),
        }
        for bike in bikes_data
        if not bike.get("is_disabled", False)
    ]

    # Sort bikes by distance and then by current_range_meter in descending order
    valid_bikes.sort(key=lambda x: (x["distance"], -x["current_range_meter"]))
    return valid_bikes[:5]


def main():
    bike_api_url = (
        "https://gbfs.omega.fifteen.eu/gbfs/2.2/marseille/en/free_bike_status.json"
    )
    station_api_url = (
        "https://gbfs.omega.fifteen.eu/gbfs/2.2/marseille/en/station_information.json"
    )
    user_coords = get_user_coordinates()
    if not user_coords:
        return

    bike_data = fetch_bike_data(bike_api_url)
    station_data = fetch_station_data(station_api_url)
    if not bike_data or "data" not in bike_data or "bikes" not in bike_data["data"]:
        print("No bike data available.")
        return

    closest_bikes = find_closest_bikes(user_coords, bike_data["data"]["bikes"])
    if closest_bikes:
        print("Les 5 vélos les plus proches sont :")
        for bike in closest_bikes:
            station_name = get_station_name(bike.get("station_id"), station_data)
            print(
                f"ID vélo : {bike['bike_id']}, Distance: {bike['distance']:.2f} mètres, "
                f"Batterie : {round((bike['current_range_meter']/45000)*100)} %, Station: {station_name}"
            )

        # Create a map centered at the user's location
        user_map = folium.Map(location=user_coords, zoom_start=18)

        # Add a marker for the user's location
        folium.Marker(
            location=user_coords,
            popup="Your Location",
            icon=folium.Icon(color="blue"),
        ).add_to(user_map)

        # Add markers for the closest bikes
        for bike in closest_bikes:
            station_name = get_station_name(bike.get("station_id"), station_data)
            folium.Marker(
                location=(bike["latitude"], bike["longitude"]),
                popup=(
                    f"ID vélo: {bike['bike_id']}<br>"
                    f"Distance: {bike['distance']:.2f} mètres<br>"
                    f"Batterie: {round((bike['current_range_meter']/45000)*100)} %<br>"
                    f"Station: {station_name}"
                ),
                icon=folium.Icon(color="green"),
            ).add_to(user_map)

        # Save the map to an HTML file and notify the user
        map_file = "closest_bikes_map.html"
        user_map.save(map_file)
        print(f"Une carte affichant les vélos les plus proches a été sauvegardée ici : {map_file}.")
    else:
        print("Pas de vélo trouvé.")


if __name__ == "__main__":
    main()
    webbrowser.open("closest_bikes_map.html")
