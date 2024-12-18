from shapely.geometry import LineString
import folium
import requests
import os
import polyline

def get_route_from_graphhopper(start_lat, start_lon, end_lat, end_lon, tolerance=0.0001):
    """
    Fetch optimized route data from GraphHopper and simplify the polyline.
    
    Parameters:
        start_lat (float): Latitude of the start location.
        start_lon (float): Longitude of the start location.
        end_lat (float): Latitude of the destination location.
        end_lon (float): Longitude of the destination location.
        tolerance (float): Tolerance for simplifying the polyline (lower is more detailed).
    
    Returns:
        list: Simplified coordinates of the route.
    """
    url = f'http://localhost:8989/route?point={start_lat},{start_lon}&point={end_lat},{end_lon}&profile=car&points_encoded=true'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        route_data = response.json()

        coordinates = []
        if 'paths' in route_data and len(route_data['paths']) > 0:
            encoded_points = route_data['paths'][0].get('points', '')
            if encoded_points:
                decoded_points = polyline.decode(encoded_points)
                print(f"Decoded points: {decoded_points}")
                
                # Used Shapely to simplify the polyline with the given tolerance
                line = LineString(decoded_points)
                simplified_line = line.simplify(tolerance=tolerance, preserve_topology=True)
                print(f"Simplified points: {list(simplified_line.coords)}")
                
                coordinates = list(simplified_line.coords)

        return coordinates

    except requests.exceptions.RequestException as e:
        print(f"Error fetching route data: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing response: {e}")
        return []

def generate_map(optimized_data, output_file='outputs/optimized_routes_map.html'):
    """
    Generate an interactive map with delivery routes using Folium.
    
    Parameters:
        optimized_data (DataFrame): The optimized delivery route data containing latitude and longitude.
        output_file (str): The path to save the generated HTML map.
    """
    # Ensure the dataframe has at least one record
    if optimized_data.empty:
        print("No optimized data available.")
        return

    start_lat, start_lon = optimized_data.iloc[0]['vehicle_gps_latitude'], optimized_data.iloc[0]['vehicle_gps_longitude']
    end_lat, end_lon = optimized_data.iloc[-1]['vehicle_gps_latitude'], optimized_data.iloc[-1]['vehicle_gps_longitude']
    
    # Got optimized route from GraphHopper
    coordinates = get_route_from_graphhopper(start_lat, start_lon, end_lat, end_lon)

    if coordinates:
        # Calculated center of the route to center the map
        latitude_center = sum([lat for lat, lon in coordinates]) / len(coordinates)
        longitude_center = sum([lon for lat, lon in coordinates]) / len(coordinates)

        m = folium.Map(location=[latitude_center, longitude_center], zoom_start=12, tiles="OpenStreetMap")

        folium.PolyLine(locations=coordinates, color="blue", weight=2.0, opacity=0.8).add_to(m)

        start_lat, start_lon = coordinates[0]
        folium.Marker(location=[start_lat, start_lon], popup="Start", icon=folium.Icon(color="green", icon="play")).add_to(m)

        end_lat, end_lon = coordinates[-1]
        folium.Marker(location=[end_lat, end_lon], popup="Arrive at destination", icon=folium.Icon(color="red", icon="stop")).add_to(m)

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the map to an HTML file
        m.save(output_file)

