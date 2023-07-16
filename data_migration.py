from libraries import st
from database import *

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