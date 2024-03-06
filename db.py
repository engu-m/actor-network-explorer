import os
import dotenv


from pymongo import MongoClient
import certifi as ca

dotenv.load_dotenv(override=True)

MONGO_DB_USERNAME = os.getenv("MONGO_DB_USERNAME")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")

MONGO_DB_URI = (
    f"mongodb+srv://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@cluster0.al87eqp.mongodb.net/"
)


client = MongoClient(MONGO_DB_URI, tls=True, tlsCAFile=ca.where())
database = client.imdb
