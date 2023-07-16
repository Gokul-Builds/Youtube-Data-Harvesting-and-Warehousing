from libraries import MongoClient, pymysql

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