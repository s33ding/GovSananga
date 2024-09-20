import numpy as np
import pandas as pd

# Function to calculate Euclidean distance between two points
def order_df(df):
    return df.sort_values(by=["group","order"], ascending=True)

# Function to calculate Euclidean distance between two points
def calculate_distance(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

# Function to sort coordinates and assign order and total number of coordinates
def assign_order_and_total(df):
    df['order'] = -1  # Placeholder for the order column
    df['total_coordinates'] = 0  # Placeholder for total coordinates in each group

    unique_groups = df['group'].unique()

    for group in unique_groups:
        group_df = df[df['group'] == group].copy()  # Get all rows with the same group
        coordinates = list(group_df['coordinates'])

        order = [-1] * len(coordinates)  # Initialize order array

        # Sort based on proximity logic
        sorted_coords = [coordinates.pop(0)]  # Start with the first point
        order[0] = 0  # First coordinate gets order 0
        remaining_indices = list(range(1, len(order)))  # Track original indices of remaining points

        for i in range(1, len(order)):
            last_point = sorted_coords[-1]
            distances = [calculate_distance(last_point, coordinates[idx]) for idx in range(len(coordinates))]
            closest_point_index = np.argmin(distances)  # Find the closest point
            sorted_coords.append(coordinates[closest_point_index])  # Add closest point to sorted list
            order[remaining_indices[closest_point_index]] = i  # Assign the order
            coordinates.pop(closest_point_index)  # Remove used point from coordinates
            remaining_indices.pop(closest_point_index)  # Remove the index of the closest point

        # Update the order and total columns for this group
        df.loc[df['group'] == group, 'order'] = order
        df.loc[df['group'] == group, 'total_coordinates'] = len(order)
    df = order_df(df)

    return df

