from pymongo import MongoClient
import configuration

# connection_params = configuration.connection_params

#connect to mongodb
mongoconnection = MongoClient("mongodb+srv://vedantatrivedi:VITChennai@tarpcluster.ssq43.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


db = mongoconnection.users
usersdb = db["trusted"]
# usersCollection = db["users"]
# usersCollection.users.update_many({"trustedUsers": {"$exists": False}}, {"$set": {"trustedUsers": []}})

# tester = { "name": "test", "username": "test", "email":"test@gmail.com","users":[] }
# usersdb.insert_one(tester)
