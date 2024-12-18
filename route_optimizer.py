import networkx as nx
import pandas as pd

def filter_southern_california_data(dataset):
    """
    Filter the dataset to include only data from Southern California.
    Southern California is defined by latitude (32.5° to 34.5°) and longitude (-118° to -116°).
    Also removes invalid coordinates outside the valid latitudes/longitudes range.
    """
    lat_min, lat_max = 32.5, 34.5  # Southern California latitude range
    lon_min, lon_max = -118.0, -116.0  # Southern California longitude range
    

    dataset = dataset[(dataset['vehicle_gps_latitude'] >= -90) & (dataset['vehicle_gps_latitude'] <= 90)]
    dataset = dataset[(dataset['vehicle_gps_longitude'] >= -180) & (dataset['vehicle_gps_longitude'] <= 180)]
    

    return dataset[(dataset['vehicle_gps_latitude'] >= lat_min) & 
                   (dataset['vehicle_gps_latitude'] <= lat_max) &
                   (dataset['vehicle_gps_longitude'] >= lon_min) & 
                   (dataset['vehicle_gps_longitude'] <= lon_max)]

def optimize_route(data):
    """
    Optimize delivery routes using traffic congestion as weights.
    Returns optimized delivery points.
    """

    data = filter_southern_california_data(data)
    

    selected_columns = ['vehicle_gps_latitude', 'vehicle_gps_longitude', 'traffic_congestion_level']
    data = data[selected_columns].dropna()
    

    G = nx.Graph()


    for i, row in data.iterrows():
        G.add_node(i, pos=(row['vehicle_gps_latitude'], row['vehicle_gps_longitude']))


    for i in range(len(data) - 1):
        weight = data.iloc[i]['traffic_congestion_level'] + 1  
        G.add_edge(i, i + 1, weight=weight)


    start_node = 0
    end_node = len(data) - 1
    shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')


    optimized_data = data.iloc[shortest_path].reset_index(drop=True).head(10)  # Limit to top 10 points for visualization
    print(f"Optimized Path: {shortest_path}")

    return optimized_data
