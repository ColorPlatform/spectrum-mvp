
import pymongo
from bson.py3compat import (_unicode)

database_host = "localhost:27017"
client = pymongo.MongoClient(host='mongodb://' + database_host)
print(client.list_database_names())

database = client["WALLETSDB"]
print(database.list_collection_names())
collection = database[_unicode("wallets")]

everything = collection.find()
print(everything.next())
print(everything.next())
print(everything.next())
print(everything.next())
print(everything.next())