ADS-B Multilateration for Aircraft Position Estimation

This project focuses on estimating an aircraft's position using multilateration based on ADS-B tower reception times. The method calculates the aircraft's position by processing the signal arrival times at multiple ground stations and applying the principles of geometry and optimization.
Project Overview
The Python script is designed to calculate an aircraft’s location by receiving inputs from several ADS-B towers. These towers provide the time it takes for a signal from the aircraft to reach them. By using this information, along with geographic coordinates, the system determines the aircraft's estimated position.
The project utilizes the Nelder-Mead optimization method to minimize the difference between the expected signal arrival time and the actual time. It also offers a visualization feature that plots both the ADS-B towers and the aircraft on a map.
Key Features:

•	Coordinate Conversion: The script supports conversion between DMS (Degrees, Minutes, Seconds) and Decimal Degrees, allowing for flexible input.

•	Distance Calculation: The Haversine formula is used to calculate the distance between two geographical points on Earth.

•	Multilateration Algorithm: The script performs iterative optimization to calculate the aircraft's position using signal reception times.

•	Data Visualization: A plot is generated that displays the positions of the ADS-B towers and the estimated aircraft location using matplotlib.
Setup and Installation

To get started, clone the repository to your local machine and install the necessary dependencies.

git clone https://github.com/your-username/ADS-B_Multilateration.git

pip install numpy matplotlib scipy

Once the dependencies are installed, you can execute the Python script:

python multilateration_adsb.py

How to Use

1.	Input ADS-B Tower Coordinates: The script will prompt you to enter the coordinates of each ADS-B tower in DMS format (e.g., 20°15'46"N 85°48'12"E).
2.	Input Reception Times: You will then enter the reception time for each tower in seconds (e.g., 0.002345678 s).
3.	Position Estimation: The script will calculate the aircraft's position using multilateration and display the estimated location in both Decimal Degrees and DMS format.
4.	Visualization: A graph will be displayed showing the positions of the ADS-B towers and the estimated aircraft.
   
Example

Enter coordinates for ADS-B tower 1 (in DMS): 20°15'46"N 85°48'12"E

Enter time of reception at ADS-B tower 1 (in seconds): 0.002345678

After providing the inputs for all towers, the output will display the estimated aircraft position along with a graphical representation of the setup.
