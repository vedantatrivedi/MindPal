from app import app
from flask import request, session
from helpers.database import *
from helpers.hashpass import *
from helpers.mailer import *
from helpers.nlp import *
from bson import json_util, ObjectId
from datetime import datetime
import calendar
import json
import numpy as np


def checkOAuthToken():

    # Currently no token present
    if(oauthdb.OAuth_tokens.count() == 0):
        return False

    return True

def putOAuthToken(credentials):

    # Clear older entries
    oauthdb.OAuth_tokens.delete_many({})

    # Insert new entry
    oauthdb.OAuth_tokens.insert_one(json.loads(json_util.dumps(credentials)))


def getOAuthToken():
    return oauthdb.OAuth_tokens.find_one()


