from pymongo import MongoClient
import configuration

# connection_params = configuration.connection_params

#connect to mongodb
mongoconnection = MongoClient("mongodb+srv://vedantatrivedi:VITChennai@tarpcluster.ssq43.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


db = mongoconnection.users
