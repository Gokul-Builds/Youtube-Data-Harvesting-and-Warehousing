from libraries import st, pd
from database import *

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