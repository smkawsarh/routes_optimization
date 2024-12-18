import pandas as pd
from route_optimizer import optimize_route  
from map_visualizer import generate_map  


dataset = pd.read_csv("E:/delivery_route_project/data/logistics_dataset.csv")  

lat_min, lat_max = 32.5, 34.5  # Southern California latitude range
lon_min, lon_max = -118.0, -116.0  # Southern California longitude range


southern_california_data = dataset[(dataset['vehicle_gps_latitude'] >= lat_min) & 
                                   (dataset['vehicle_gps_latitude'] <= lat_max) & 
                                   (dataset['vehicle_gps_longitude'] >= lon_min) & 
                                   (dataset['vehicle_gps_longitude'] <= lon_max)]


if southern_california_data.empty:
    print("No data available for Southern California region.")
else:
    optimized_data = optimize_route(southern_california_data)
    if optimized_data is not None and 'vehicle_gps_latitude' in optimized_data.columns and 'vehicle_gps_longitude' in optimized_data.columns:

        generate_map(optimized_data)
    else:
        print("Error: Optimized data is missing required columns or is invalid.")
