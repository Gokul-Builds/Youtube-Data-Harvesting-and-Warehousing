# YouTube Data Harvesting and Warehousing Program

This program allows you to retrieve data from YouTube channels, store it in a MongoDB database, and migrate it to a MySQL database for further analysis. It also provides data visualization capabilities.

## Prerequisites

- Python 3.6 or above
- MongoDB installed and running on localhost
- MySQL installed and running on localhost
- Required Python libraries (listed in requirements.txt)

## Installation

1. Clone the repository:
    https://github.com/Gokul-Builds/Youtube-Data-Harvesting-and-Warehousing.git


2. Install the required Python libraries:
    pip install -r requirements.txt


3. Update the API Key:
    - Open the file `youtube_api.py` in the project directory.
    - Replace the placeholder text "Enter your API key" with your actual YouTube API key.

## Usage

1. Run the `main.py` file:
    python main.py

2. In the Streamlit app, enter the YouTube channel IDs (one per line) and click the "Retrieve Data" button to fetch channel information and video data.

3. Optionally, click the "Migrate Data to MySQL" button to transfer the collected data from MongoDB to a MySQL database.

4. Use the "Visualize Data" button to generate visualizations based on the data stored in the MySQL database. Enter the channel name for which you want to visualize the data.

## File Structure

- `database.py`: Contains functions for connecting to MongoDB and MySQL databases.
- `youtube_api.py`: Handles interactions with the YouTube Data API for retrieving channel data and video statistics.
- `visualization.py`: Provides functions for visualizing the collected data using Matplotlib and Streamlit.
- `data_migration.py`: Provides the function for migrating data stored in MongoDB to MySQL database.
- `libraries.py`: Contains the list of python libraries for the program that is shared among all the files.
- `main.py`: The main program file that orchestrates the data retrieval, migration, and visualization processes.
