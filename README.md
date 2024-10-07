ADS-B Multilateration for Aircraft Position Estimation

Project Overview
The ADS-B Multilateration for Aircraft Position Estimation project is dedicated to accurately determining an aircraft's position using multilateration techniques based on ADS-B (Automatic Dependent Surveillance-Broadcast) tower reception times. By processing the signal arrival times at multiple ground stations, the system applies geometric principles and optimization algorithms to estimate the aircraft's location. Additionally, the project offers a visualization feature that plots both the ADS-B towers and the aircraft on an interactive map, providing a clear and intuitive representation of the data.

Key Features
This project encompasses several key features that contribute to its functionality and usability. It includes coordinate conversion capabilities, allowing users to input geographical data in both DMS (Degrees, Minutes, Seconds) and Decimal Degrees formats. The Haversine formula is employed to calculate the distance between two geographical points on Earth, ensuring precise distance measurements. The core of the project lies in its multilateration algorithm, which utilizes the Nelder-Mead optimization method to minimize discrepancies between expected and actual signal arrival times, thereby accurately estimating the aircraft's position. Furthermore, the project integrates data visualization tools, generating graphical representations that display the positions of ADS-B towers and the estimated aircraft location using libraries like matplotlib and dash-leaflet for interactive maps.

Technologies Used
The project leverages a range of technologies to achieve its objectives effectively. Python serves as the core programming language, facilitating data processing and algorithm implementation. The project utilizes Dash by Plotly to build an interactive web application, enhancing user interaction and real-time data visualization. Dash Leaflet is integrated for dynamic map visualizations, providing an intuitive geographical representation of the data. NumPy and Pandas are employed for numerical computations and data manipulation, respectively. SciPy offers optimization algorithms crucial for the multilateration process, while Matplotlib contributes to data visualization and plotting. Additionally, Dash Bootstrap Components are used to style the web application with responsive and aesthetically pleasing Bootstrap themes.

Setup and Installation
To get started with the project, follow these steps:

1. Clone the Repository

Begin by cloning the repository to your local machine using the following command:

git clone https://github.com/your-username/ADS-B_Multilateration.git
cd ADS-B_Multilateration

2. Create a Virtual Environment (Optional but Recommended)

Creating a virtual environment ensures that dependencies are managed effectively without affecting your global Python installation.

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies

Install the necessary Python packages required for the project.

pip install numpy matplotlib scipy pandas dash dash-leaflet dash-bootstrap-components

4. Prepare the ADS-B Data

Ensure that you have the adsb_data.csv file in the project directory. This CSV file should contain the required columns:

Serial No.
Aircraft ID
Heading
Ground Speed (knots)
Time at Tower 1 (sec)
Time at Tower 2 (sec)
Time at Tower 3 (sec)
Time at Tower 4 (sec)
Time at Tower 5 (sec)
This data is essential for the multilateration algorithm to estimate the aircraft's position accurately.
