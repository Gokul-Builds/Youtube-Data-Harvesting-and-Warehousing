from libraries import build, st, HttpError
from database import mongo_collection

API_KEY = "Enter Your Google API Key"
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