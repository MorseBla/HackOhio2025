import math

def haversine_distance(coord1, coord2):
    """
    Returns the great-circle distance between two GPS coordinates (lat, lon) in meters.
    """
    R = 6371000  # Earth radius in meters
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def find_closest_coordinate(target_coord, coord_list):
    """
    Given a target GPS coordinate (lat, lon) and a list of coordinate pairs [(lat, lon), ...],
    returns the closest coordinate and its distance (in meters).
    """
    if not coord_list:
        raise ValueError("Coordinate list is empty.")
    
    closest_coord = None
    min_distance = float('inf')

    for coord in coord_list:
        dist = haversine_distance(target_coord, coord)
        if dist < min_distance:
            min_distance = dist
            closest_coord = coord
    
    return closest_coord, min_distance


target = (40.0076, -83.0300)  # say, The Oval at OSU
rooms = [
    (40.0029, -83.0158),  # Knowlton Hall
    (40.0049, -83.0283),  # Thompson Library
    (40.0063, -83.0304),  # Mirror Lake
]

closest, distance = find_closest_coordinate(target, rooms)
print(f"Closest room: {closest} ({distance:.1f} meters away)")
