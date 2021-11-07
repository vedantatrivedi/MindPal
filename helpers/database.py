from pymongo import MongoClient
import os

# import configuration
# connection_params = configuration.connection_params

#connect to mongodb
mongoconnection = MongoClient(os.environ['MONGODB'])

# Databases
db = mongoconnection.users
usersdb = db["trusted"]
oauthdb = mongoconnection.OAuth_tokens 