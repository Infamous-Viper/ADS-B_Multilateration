import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import re

# Speed of light in meters per second
speed_of_light = 3e8

# Function to convert DMS (Degrees, Minutes, Seconds) to decimal degrees
def dms_to_decimal(dms_string):
    pattern = re.compile(r"(\d+)°(\d+)'(\d+)\"([NS])\s+(\d+)°(\d+)'(\d+)\"([EW])")
    match = pattern.match(dms_string)
    
    if match:
        lat_deg = int(match.group(1))
        lat_min = int(match.group(2))
        lat_sec = int(match.group(3))
        lat_dir = match.group(4)
        
        lon_deg = int(match.group(5))
        lon_min = int(match.group(6))
        lon_sec = int(match.group(7))
        lon_dir = match.group(8)
        
        lat_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
        lon_decimal = lon_deg + lon_min / 60 + lon_sec / 3600
        
        if lat_dir == 'S':
            lat_decimal = -lat_decimal
        if lon_dir == 'W':
            lon_decimal = -lon_decimal
        
        return lat_decimal, lon_decimal
    else:
        raise ValueError("Invalid DMS format. Please enter the coordinates in the correct format.")

# Function to convert decimal degrees back to DMS format
def decimal_to_dms(decimal_lat, decimal_lon):
    def convert_to_dms(decimal, is_latitude=True):
        degrees = int(decimal)
        minutes = int((abs(decimal) - abs(degrees)) * 60)
        seconds = (abs(decimal) - abs(degrees) - minutes / 60) * 3600
        direction = ''
        
        if is_latitude:
            direction = 'N' if degrees >= 0 else 'S'
        else:
            direction = 'E' if degrees >= 0 else 'W'
        
        return f"{abs(degrees)}°{minutes}'{round(seconds):02d}\"{direction}"

    lat_dms = convert_to_dms(decimal_lat, is_latitude=True)
    lon_dms = convert_to_dms(decimal_lon, is_latitude=False)
    
    return lat_dms, lon_dms

# Function to calculate the distance between two points (lat, lon) using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# Input for the number of ADS-B towers
num_towers = int(input("Enter the number of ADS-B towers: "))

adsb_towers = []
reception_times = []

# Input coordinates of each tower and reception times
for i in range(num_towers):
    dms_input = input(f"\nEnter coordinates for ADS-B tower {i+1} (in format '20°15'46\"N 85°48'12\"E'): ").strip()
    lat_decimal, lon_decimal = dms_to_decimal(dms_input)
    
    adsb_towers.append((lat_decimal, lon_decimal))

    time = float(input(f"Enter time of reception at ADS-B tower {i+1} (in seconds): "))
    reception_times.append(time)

# Assume the transmission time (we will optimize to find the best estimate)
transmission_time = 0  # For simplification, we assume time 0 or treat it as a known constant

# Multilateration: Define the error function to minimize
def error_function(estimated_position, adsb_towers, reception_times, transmission_time):
    errors = []
    for i, (lat, lon) in enumerate(adsb_towers):
        dist = haversine(estimated_position[0], estimated_position[1], lat, lon)
        estimated_time_of_arrival = transmission_time + dist / speed_of_light
        errors.append((reception_times[i] - estimated_time_of_arrival)**2)
    return np.sum(errors)

# Calculate the centroid of the ADS-B towers for the initial guess
centroid_lat = np.mean([lat for lat, lon in adsb_towers])
centroid_lon = np.mean([lon for lat, lon in adsb_towers])
initial_guess = (centroid_lat, centroid_lon)

# Perform minimization to estimate aircraft position with improved precision
result = minimize(
    error_function,
    initial_guess,
    args=(adsb_towers, reception_times, transmission_time),
    method='Nelder-Mead',  # More stable for this kind of optimization
    options={'xatol': 1e-10, 'fatol': 1e-10, 'maxiter': 10000}
)

# Estimated aircraft position in decimal degrees
estimated_aircraft_position = result.x

# Convert estimated position to DMS format for output
estimated_lat_dms, estimated_lon_dms = decimal_to_dms(estimated_aircraft_position[0], estimated_aircraft_position[1])

# Plotting the ADS-B towers and estimated aircraft position
plt.figure(figsize=(10, 8))

# Plot ADS-B towers
adsb_lats, adsb_lons = zip(*adsb_towers)
plt.scatter(adsb_lons, adsb_lats, color='red', label='ADS-B Towers', marker='^', s=100)

# Plot the estimated aircraft location
plt.scatter(estimated_aircraft_position[1], estimated_aircraft_position[0], color='blue', label='Estimated Aircraft', marker='o', s=100)

# Add labels to each ADS-B tower
for i, (lat, lon) in enumerate(adsb_towers, start=1):
    plt.text(lon, lat, f'ADS-B {i}', fontsize=12, ha='right')

# Add label for the aircraft
plt.text(estimated_aircraft_position[1], estimated_aircraft_position[0], 'Aircraft', fontsize=12, ha='left')

# Set plot title and labels
plt.title('Aircraft Position Estimation Using Multilateration')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Add legend
plt.legend()

# Show grid and plot
plt.grid(True)
plt.show()

# Output the result
print("\n### Result Summary ###")
for i, (lat, lon) in enumerate(adsb_towers):
    lat_dms, lon_dms = decimal_to_dms(lat, lon)
    print(f"ADS-B {i+1} - {lat_dms} {lon_dms}    TIME: {reception_times[i]:.9f} s")

# Print estimated aircraft position in Decimal Degrees
print(f"\nEstimated Aircraft Position in Decimal Degrees: {estimated_aircraft_position[0]:.6f}, {estimated_aircraft_position[1]:.6f}")

# Print estimated aircraft position in DMS
print(f"Estimated Aircraft Position in DMS: {estimated_lat_dms}, {estimated_lon_dms}")
