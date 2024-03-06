import os
import dotenv


from pymongo import MongoClient
import certifi as ca

dotenv.load_dotenv(override=True)

MONGO_DB_URI = os.getenv("MONGO_DB_URI")


client = MongoClient(MONGO_DB_URI, tls=True, tlsCAFile=ca.where())
database = client.imdb
