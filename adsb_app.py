# adsb_app.py

import numpy as np
from dash import Dash, html, dcc, Output, Input
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import pandas as pd
from scipy.optimize import minimize

# Speed of light in meters per second
speed_of_light = 3e8

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points (lat, lon) using the Haversine formula."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = phi2 - phi1
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def multilateration(adsb_towers, reception_times):
    """Performs multilateration to estimate the aircraft's position."""
    def error_function(estimated_position):
        errors = []
        for (lat, lon), t in zip(adsb_towers, reception_times):
            dist = haversine(estimated_position[0], estimated_position[1], lat, lon)
            estimated_time_of_arrival = dist / speed_of_light
            errors.append((t - estimated_time_of_arrival)**2)
        return np.sum(errors)  # Corrected indentation

    # Initial guess: centroid of ADS-B towers
    initial_guess = np.mean(adsb_towers, axis=0)

    result = minimize(
        error_function, initial_guess, method='Nelder-Mead',
        options={'xatol': 1e-8, 'fatol': 1e-8, 'maxiter': 10000}
    )

    if result.success:
        return result.x
    else:
        return None

# ADS-B tower coordinates (latitude, longitude)
adsb_towers = np.array([
    [20.26278, 85.80333],  # ADS-B 1
    [20.26028, 85.81222],  # ADS-B 2
    [20.24861, 85.82361],  # ADS-B 3
    [20.23917, 85.82139],  # ADS-B 4
    [20.24000, 85.81194],  # ADS-B 5
])

def read_data_from_csv(file_path='adsb_data.csv'):
    """Reads data from a local CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Ensure the DataFrame has the required columns
        expected_columns = [
            'Serial No.', 'Aircraft ID', 'Heading', 'Ground Speed (knots)',
            'Time at Tower 1 (sec)', 'Time at Tower 2 (sec)',
            'Time at Tower 3 (sec)', 'Time at Tower 4 (sec)',
            'Time at Tower 5 (sec)'
        ]
        if not all(col in df.columns for col in expected_columns):
            print("CSV file is missing required columns.")
            return []
        # Convert DataFrame to list of lists
        data = df[expected_columns].values.tolist()
        return data
    except Exception as e:
        print(f"Error reading data from CSV: {e}")
        return []

def main():
    # Initialize Dash app with a Bootstrap theme
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    server = app.server  # For deploying to platforms like Heroku

    # Define the layout
    app.layout = dbc.Container([
        # Header with a Navbar component
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand("ADS-B Aircraft Position Estimation", className='mx-auto', style={
                    'color': 'black',
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'width': '100%',
                }),
            ]),
            color=None,  # No predefined color to allow custom background color
            dark=False,
            style={'backgroundColor': '#B0E0E6'},  # Powder blue background
            className='mb-4',
        ),
        dbc.Row([
            # Sidebar
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Select Aircraft", className='text-center'),
                                   style={'backgroundColor': '#B0E0E6'}),
                    dbc.CardBody([
                        dbc.Checklist(
                            id='aircraft-checklist',
                            options=[],  # Options will be populated dynamically
                            value=[],    # Default selected values
                            style={'height': '70vh', 'overflowY': 'auto'},
                            switch=True,
                        ),
                    ]),
                ], className='mb-4 shadow', style={'borderColor': '#B0E0E6'}),
            ], width=3),
            # Main content
            dbc.Col([
                # Map
                dbc.Card([
                    dbc.CardHeader(html.H5("Aircraft Map", className='text-center'),
                                   style={'backgroundColor': '#B0E0E6'}),
                    dbc.CardBody([
                        dl.Map(center=(adsb_towers[:, 0].mean(), adsb_towers[:, 1].mean()), zoom=13, children=[
                            dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
                            dl.LayerGroup(id="layer"),
                        ], style={'width': '100%', 'height': '55vh', 'margin': "auto"}),
                    ]),
                ], className='mb-4 shadow', style={'borderColor': '#B0E0E6'}),
                # Aircraft Details
                dbc.Card([
                    dbc.CardHeader(html.H5("Aircraft Details", className='text-center'),
                                   style={'backgroundColor': '#B0E0E6'}),
                    dbc.CardBody([
                        html.Div(id='aircraft-details', style={
                            'maxHeight': '25vh',
                            'overflowY': 'auto',
                            'padding': '10px',
                        }),
                    ]),
                ], className='shadow', style={'borderColor': '#B0E0E6'}),
            ], width=9),
        ]),
        # Interval for updates
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        )
    ], fluid=True)

    @app.callback(
        [Output("layer", "children"),
         Output("aircraft-checklist", "options"),
         Output("aircraft-checklist", "value"),
         Output("aircraft-details", "children")],
        [Input("interval-component", "n_intervals"),
         Input("aircraft-checklist", "value")]
    )
    def update_map(n_intervals, selected_aircraft_ids):
        # Read data from CSV
        data = read_data_from_csv()
        if not data:
            print("No data found in the CSV file.")
            return [], [], [], ''

        aircraft_positions = []
        aircraft_options = []
        aircraft_details = []

        for row in data:
            if len(row) < 9:
                print(f"Skipping incomplete row: {row}")
                continue  # Skip incomplete rows

            serial_no, aircraft_id, heading, ground_speed, *reception_times = row
            try:
                heading = float(heading)
                ground_speed = float(ground_speed)
                reception_times = [float(t) for t in reception_times]
            except ValueError:
                print(f"Invalid data format in row: {row}")
                continue  # Skip rows with invalid data

            # Perform multilateration
            estimated_position = multilateration(adsb_towers, reception_times)
            if estimated_position is not None:
                lat, lon = estimated_position
                print(f"Aircraft {aircraft_id} estimated at Lat: {lat:.6f}, Lon: {lon:.6f}")
                aircraft_positions.append({
                    'id': aircraft_id,
                    'lat': lat,
                    'lon': lon,
                    'heading': heading,
                    'ground_speed': ground_speed
                })
                aircraft_options.append({'label': f"Aircraft {aircraft_id}", 'value': aircraft_id})
            else:
                print(f"Could not estimate position for Aircraft {aircraft_id}")

        # Update the checklist options
        checklist_options = aircraft_options
        if not selected_aircraft_ids:
            selected_aircraft_ids = [option['value'] for option in aircraft_options]
        else:
            # Ensure selected IDs are still valid
            selected_aircraft_ids = [aid for aid in selected_aircraft_ids if aid in [opt['value'] for opt in aircraft_options]]

        # Create markers for selected aircraft
        aircraft_markers = []
        for aircraft in aircraft_positions:
            if aircraft['id'] in selected_aircraft_ids:
                lat = aircraft['lat']
                lon = aircraft['lon']
                aircraft_id = aircraft['id']
                heading = aircraft['heading']
                ground_speed = aircraft['ground_speed']

                # Create a nicely formatted popup content
                popup_content = html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(f"Aircraft ID: {aircraft_id}", className="card-title"),
                            html.Hr(),
                            html.P([
                                html.Strong("Latitude: "),
                                f"{lat:.6f}"
                            ], className="card-text"),
                            html.P([
                                html.Strong("Longitude: "),
                                f"{lon:.6f}"
                            ], className="card-text"),
                            html.P([
                                html.Strong("Heading: "),
                                f"{heading}°"
                            ], className="card-text"),
                            html.P([
                                html.Strong("Ground Speed: "),
                                f"{ground_speed} knots"
                            ], className="card-text"),
                        ])
                    ], style={'width': '200px', 'backgroundColor': '#E3F2FD'})  # Light blue background
                ])

                aircraft_markers.append(
                    dl.Marker(
                        position=(lat, lon),
                        children=[
                            dl.Tooltip(html.Div([
                                html.Strong(f"Aircraft {aircraft_id}")
                            ], style={'color': 'black'})),
                            dl.Popup(popup_content)
                        ],
                        icon={
                            "iconUrl": "/assets/icons/aircraft.png",  # Path to local aircraft icon
                            "iconSize": [40, 40],
                            "iconAnchor": [20, 40],
                            "popupAnchor": [0, -40],
                        }
                    )
                )
                # Add details to the aircraft details section
                aircraft_details.append(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5(f"Aircraft ID: {aircraft_id}", className="card-title"),
                            html.Hr(),
                            html.P([
                                html.Strong("Heading: "),
                                f"{heading}°"
                            ], className="card-text"),
                            html.P([
                                html.Strong("Ground Speed: "),
                                f"{ground_speed} knots"
                            ], className="card-text"),
                        ]),
                        className='mb-3 shadow-sm',
                        style={'backgroundColor': '#E3F2FD'}  # Light blue background
                    )
                )

        return aircraft_markers, checklist_options, selected_aircraft_ids, aircraft_details

    # Run the Dash app
    app.run_server(debug=True)

if __name__ == '__main__':
    main()
