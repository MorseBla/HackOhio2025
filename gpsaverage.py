import math

def average_gps(*coords):
    """
    Takes any number of (latitude, longitude) pairs and returns the average location.
    Uses spherical averaging to account for Earth's curvature.
    
    Example:
        average_gps((40.0, -83.0), (41.0, -82.0))
    """
    if not coords:
        raise ValueError("At least one coordinate must be provided.")

    # Convert lat/lon to Cartesian coordinates (x, y, z)
    x_total = y_total = z_total = 0.0
    for lat, lon in coords:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        x_total += math.cos(lat_rad) * math.cos(lon_rad)
        y_total += math.cos(lat_rad) * math.sin(lon_rad)
        z_total += math.sin(lat_rad)

    # Average
    num_points = len(coords)
    x_avg = x_total / num_points
    y_avg = y_total / num_points
    z_avg = z_total / num_points

    # Convert back to lat/lon
    lon_avg = math.atan2(y_avg, x_avg)
    hyp = math.sqrt(x_avg**2 + y_avg**2)
    lat_avg = math.atan2(z_avg, hyp)

    return math.degrees(lat_avg), math.degrees(lon_avg)

points = [(40.0, -83.0), (41.0, -82.0), (39.5, -84.0)]
avg_lat, avg_lon = average_gps(*points)
print(f"Average location: {avg_lat:.5f}, {avg_lon:.5f}")
