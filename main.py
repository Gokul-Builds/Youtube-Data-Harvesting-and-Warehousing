#works perfecty
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pymongo
from pymongo import MongoClient
import mysql.connector
import pymysql
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pymysql.err

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["my_mongodb_database_youtube"]
mongo_collection = mongo_db["my_mongodb_collection_youtubers"]

# Connect to MySQL
mysql_conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="capstone_guvi",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)
mysql_cursor = mysql_conn.cursor()

API_KEY = "Enter your API key"

def get_channel_data(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        channels_response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()

        if 'items' not in channels_response or len(channels_response['items']) == 0:
            st.warning(f"No channel found for the ID: {channel_id}")
            return None

        channel = channels_response['items'][0]

        channel_name = channel['snippet']['title']
        subscribers = channel['statistics']['subscriberCount']
        total_videos = channel['statistics']['videoCount']

        playlists_response = youtube.playlists().list(
            part='snippet',
            channelId=channel_id,
            maxResults=1
        ).execute()

        if 'items' not in playlists_response or len(playlists_response['items']) == 0:
            st.warning(f"No playlist found for the channel ID: {channel_id}")
            return None

        playlist_id = playlists_response['items'][0]['id']

        videos = []
        next_page_token = None

        while True:
            playlist_items_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            videos.extend(playlist_items_response['items'])
            next_page_token = playlist_items_response.get('nextPageToken')

            if not next_page_token:
                break

        video_data = []

        if len(videos) > 0:
            for item in videos:
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']

                video_response = youtube.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()

                if 'items' not in video_response or len(video_response['items']) == 0:
                    # Skip adding video if no statistics available
                    continue

                video_stats = video_response['items'][0]['statistics']
                likes = video_stats.get('likeCount', 0)
                dislikes = video_stats.get('dislikeCount', 0)
                comments = video_stats.get('commentCount', 0)

                video_data.append({
                    'Video ID': video_id,
                    'Title': video_title,
                    'Likes': likes,
                    'Dislikes': dislikes,
                    'Comments': comments
                })

        document = {
            'Channel ID': channel_id,
            'Channel Name': channel_name,
            'Subscribers': subscribers,
            'Total Videos': total_videos,
            'Playlist ID': playlist_id,
            'Video Data': video_data
        }

        mongo_collection.insert_one(document)

        return {
            'Channel Name': channel_name,
            'Subscribers': subscribers,
            'Total Videos': total_videos,
            'Playlist ID': playlist_id,
            'Video Data': video_data
        }
    except HttpError as e:
        st.error("An error occurred: " + str(e))
        return None

def migrate_data_to_mysql():
    channel_data = list(mongo_collection.find({}))

    if len(list(channel_data)) == 0:
        st.warning("No data found in MongoDB.")
        return

    for channel in channel_data:
        channel_name = channel['Channel Name']
        video_data = channel['Video Data']

        # Create MySQL table for the channel data
        table_name = channel_name.lower().replace(" ", "_")
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
            `Video ID` VARCHAR(255) PRIMARY KEY,
            `Title` VARCHAR(255),
            `Likes` INT,
            `Dislikes` INT,
            `Comments` INT
            )
        """
        mysql_cursor.execute(create_table_query)

        # Insert video data into MySQL table
        for video in video_data:
            video_id = video['Video ID']
            title = video['Title']
            likes = video['Likes']
            dislikes = video['Dislikes']
            comments = video['Comments']

            insert_query = f"""
                INSERT INTO `{table_name}` (`Video ID`, `Title`, `Likes`, `Dislikes`, `Comments`)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                `Title` = VALUES(`Title`),
                `Likes` = VALUES(`Likes`),
                `Dislikes` = VALUES(`Dislikes`),
                `Comments` = VALUES(`Comments`)
            """
            mysql_cursor.execute(insert_query, (video_id, title, likes, dislikes, comments))


    mysql_conn.commit()

    st.success("Data migrated to MySQL.")

def visualize_data(channel_name):
    table_name = channel_name.lower().replace(" ", "_")

    try:
        query = f"SELECT `Title`, `Likes`, `Dislikes`, `Comments` FROM `{table_name}`"
        mysql_cursor.execute(query)
        results = mysql_cursor.fetchall()

        if len(results) == 0:
            st.warning(f"No data found for the channel: {channel_name}")
            return

        df = pd.DataFrame(results)
        df.set_index('Title', inplace=True)

        # Visualization 1: Bar Chart
        st.subheader("Likes, Dislikes, and Comments for Videos")
        st.bar_chart(df)
        st.set_option('deprecation.showPyplotGlobalUse', False)

        # Visualization 2: Line Chart
        st.subheader("Likes and Dislikes Over Time")
        st.line_chart(df[['Likes', 'Dislikes']])

        # Visualization 3: Area Chart
        st.subheader("Comments Over Time")
        st.area_chart(df['Comments'])

    except pymysql.err.Error as e:
        st.error(f"An error occurred: {e}")



def main():
    st.title("YouTube Channel Data")

    channel_ids = st.text_area("Enter YouTube Channel IDs (one per line)", height=200)
    channel_id_list = channel_ids.strip().split("\n")

    if st.button("Retrieve Data"):
        for channel_id in channel_id_list:
            if channel_id:
                st.write(f"Retrieving data for Channel ID: {channel_id}")
                channel_data = get_channel_data(channel_id)
                if channel_data is not None:
                    st.subheader("Channel Information")
                    st.write(f"Channel Name: {channel_data['Channel Name']}")
                    st.write(f"Subscribers: {channel_data['Subscribers']}")
                    st.write(f"Total Videos: {channel_data['Total Videos']}")
                    st.write(f"Playlist ID: {channel_data['Playlist ID']}")

                    st.subheader("Video Information")
                    for video in channel_data['Video Data']:
                        st.write(f"Video ID: {video['Video ID']}")
                        st.write(f"Title: {video['Title']}")
                        st.write(f"Likes: {video['Likes']}")
                        st.write(f"Dislikes: {video['Dislikes']}")
                        st.write(f"Comments: {video['Comments']}")
                        st.write("-" * 50)
                    st.write("Data stored in MongoDB.")

    if st.button("Migrate Data to MySQL"):
        migrate_data_to_mysql()

    st.title("Data Visualization")

    channel_name = st.text_input("Enter Channel Name")

    if st.button("Visualize Data"):
        visualize_data(channel_name)

if __name__ == "__main__":
    main()
