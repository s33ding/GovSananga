import numpy as np
import pandas as pd
import math

# Function to calculate Euclidean distance between two points
def order_df(df):
    return df.sort_values(by=["group","order"], ascending=True)

def drop_duplicates(df):
    df['total_coordinates'] = 0  # Placeholder for total coordinates in each group
    unique_groups = df['group'].unique()
    for group in unique_groups:
        group_df = df[df['group'] == group].copy()  # Get all rows with the same group
        group_df.drop_duplicates(subset=["coordinates"], inplace=True)
        df = df.loc[df["group"] != group]
        df = pd.concat([df, group_df])
    return df

# Function to sort coordinates and assign order and total number of coordinates
def assign_total(df):
    df['total_coordinates'] = 0  
    unique_groups = df['group'].unique()
    for group in unique_groups:
        df.loc[df['group'] == group, 'total_coordinates'] = len(df[df["group"] == group])
    return df

def assign_previous_coordinates(df):
    """
    Assigns previous coordinates within each unique group in the DataFrame based on the next_coordinates.

    Parameters:
    df (DataFrame): A DataFrame containing 'group', 'order', 'coordinates', and 'next_coordinates' columns.

    Returns:
    DataFrame: The updated DataFrame with 'previous_coordinates' assigned.
    """
    # Initialize the 'previous_coordinates' column
    df["previous_coordinates"] = None

    # Loop through each unique group to assign previous coordinates within each group
    for gr in df["group"].unique():
        group_df = df[df["group"] == gr]

        # Create a dictionary where the keys are the `next_coordinates` and the values are the `coordinates`
        next_to_previous_map = {row["next_coordinates"]: row["coordinates"] for _, row in group_df.iterrows()}

        # Map the previous_coordinates using the next_to_previous_map dictionary
        df.loc[df["group"] == gr, "previous_coordinates"] = df[df["group"] == gr]["coordinates"].map(next_to_previous_map)

    return df

def assign_next_coordinates(df):
    """
    Assigns next coordinates within each unique group in the DataFrame.

    Parameters:
    df (DataFrame): A DataFrame containing 'group', 'order', 'coordinates', and 'next_coordinates' columns.

    Returns:
    DataFrame: The updated DataFrame with 'next_coordinates' assigned.
    """
    # Initialize the 'next_coordinates' column
    df["next_coordinates"] = None

    # Loop through each unique group to assign next coordinates within each group
    for gr in df["group"].unique():
        # Filter the DataFrame for the current group and sort by order
        group_df = df[df["group"] == gr].sort_values(by="order", ascending=True).reset_index()

        # Iterate through the group_df and assign the next coordinate
        for i in range(len(group_df) - 1):
            # Get the index of the current row in the original DataFrame
            original_index = group_df.loc[i, "index"]
            # Get the next coordinate
            next_coordinates = group_df.loc[i + 1, "coordinates"]

            # Check if the current coordinates are equal to the next coordinates
            current_coordinates = group_df.loc[i, "coordinates"]
            next_index = i + 1

            # Continue to look for the next unique coordinates if they are equal
            while next_index < len(group_df) and current_coordinates == next_coordinates:
                next_index += 1
                if next_index < len(group_df):
                    next_coordinates = group_df.loc[next_index, "coordinates"]

            # If we reached the end, next_coordinates should be None
            if next_index >= len(group_df):
                next_coordinates = None

            # Assign the next coordinates to the original DataFrame using the correct index
            df.at[original_index, "next_coordinates"] = next_coordinates

    return df

# Function to calculate the heading between two coordinates
def calculate_heading(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    initial_heading = math.atan2(x, y)

    # Convert from radians to degrees and normalize to 0-360
    heading = math.degrees(initial_heading)
    heading = (heading + 360) % 360

    return heading

# Function to calculate the Haversine distance between two points
def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance

def weighted_moving_average_heading(df, window=5):
    """
    Smooth the heading values in the DataFrame using a weighted moving average.

    Parameters:
    df (pd.DataFrame): Input DataFrame with 'heading' column.
    window (int): Size of the moving window to calculate the weighted average.

    Returns:
    pd.DataFrame: DataFrame with smoothed 'heading' values.
    """
    # Check if the 'heading' column exists
    if 'heading' not in df.columns:
        raise ValueError("The DataFrame must contain a 'heading' column.")

    # Convert heading to radians for circular smoothing
    df['heading_rad'] = df['heading'].apply(lambda x: math.radians(x))

    # Calculate the weighted moving average for both sin and cos components
    weights = list(range(1, window + 1))
    weight_sum = sum(weights)

    def weighted_average(series):
        return (series * weights[-len(series):]).sum() / weight_sum

    df['sin_heading'] = df['heading_rad'].apply(math.sin).rolling(window=window, min_periods=1).apply(weighted_average, raw=True)
    df['cos_heading'] = df['heading_rad'].apply(math.cos).rolling(window=window, min_periods=1).apply(weighted_average, raw=True)

    # Calculate the smoothed heading by converting back to degrees
    df['heading'] = df.apply(lambda row: math.degrees(math.atan2(row['sin_heading'], row['cos_heading'])), axis=1)

    # Ensure all headings are between 0 and 360 degrees
    df['heading'] = df['heading'].apply(lambda x: (x + 360) % 360)

    # Drop temporary columns used for smoothing
    df.drop(columns=['heading_rad', 'sin_heading', 'cos_heading'], inplace=True)

    return df

# Function to add heading column to DataFrame
def add_heading_column(df):
    for i in range(len(df) - 1):
        coord1 = df['coordinates'].iloc[i]
        coord2 = df['next_coordinates'].iloc[i]
        if pd.isna(coord2):
            pass
        else:
            heading = calculate_heading(coord1, coord2)
            df['heading'].iloc[i] = heading
    df = df.ffill()
    df = weighted_moving_average_heading(df, window=3)
    return df

# Function to order coordinates and return a DataFrame with the new "order" column
def calculate_heading_in_all_groups(df):
    unique_groups = df['group'].unique()
    df["heading"] = None
    for group in unique_groups:
        group_df = df[df['group'] == group].copy()  # Get all rows with the same group
        group_df = add_heading_column(group_df)
        df = df.loc[df["group"] != group]
        df = pd.concat([df, group_df])
    return df

# Function to order coordinates and return a DataFrame with the new "order" column
def add_order_column_in_all_groups(df):
    unique_groups = df['group'].unique()
    for group in unique_groups:
        group_df = df[df['group'] == group].copy()  # Get all rows with the same group
        group_df = add_order_column(group_df)
        df = df.loc[df["group"] != group]
        df = pd.concat([df, group_df])
    return df

def add_order_column(df):
    # Extract the list of coordinates
    coordinates = df['coordinates'].tolist()
    # Store original indexes to map back later
    original_indexes = list(df.index)
    # Order the coordinates
    ordered_coordinates = [coordinates.pop(0)]
    original_order = [original_indexes.pop(0)]
    
    while coordinates:
        last_coord = ordered_coordinates[-1]
        # Find the nearest coordinate
        nearest_index = min(range(len(coordinates)), key=lambda i: calculate_distance(last_coord, coordinates[i]))
        nearest_coord = coordinates.pop(nearest_index)
        ordered_coordinates.append(nearest_coord)
        original_order.append(original_indexes.pop(nearest_index))
    
    # Create a mapping of original indexes to order
    order_mapping = {index: order for order, index in enumerate(original_order)}
    # Add the "order" column to the DataFrame
    df['order'] = df.index.map(order_mapping)
    df['order'] = df["order"].astype(int)
    return df

