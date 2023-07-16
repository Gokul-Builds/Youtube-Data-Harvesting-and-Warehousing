from libraries import st, MongoClient, pymysql, build, HttpError, pd
from database import *
from youtube_api import *
from data_migration import *
from visualization import *

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
