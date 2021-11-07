from app import app
from flask import request, session
from helpers.database import *
from helpers.hashpass import *
from helpers.nlp import *
from bson import json_util, ObjectId
from datetime import datetime
import calendar
import json
import numpy as np

def checkTrustedUsername():
    username = request.form["username"]
    check = db.trusted.find_one({"username": username})
    if check is None:
        return "No User"
    else:
        return "User exists"


def checkTrustedPassword():

    username = request.form["username"]
    check = db.trusted.find_one({"username": username})

    if(check == None):
        return "wrong"

    password = request.form["password"]
    hashpassword = getHashed(password)

    if hashpassword == check["password"]:
        session["trusted_users"] = username
        session["trusted_users_email"] = check["email"]
        print(session)
        return "correct"
    else:
        return "wrong"
    
def createTrustedUser(username):
    
    exist_count = db.trusted.find({"username": request.form["username"]}).count()

    if(exist_count > 0):
        trustedDoc = db.trusted.find_one({"username": request.form["username"]})
        return trustedDoc['email']

    fields = [k for k in request.form]
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    data['password']= ''
    data['isConfirmed'] = False
    data['hashedUsername'] = getHashed(request.form.get("username"))
    
    myquery = { "username": username }
    userDoc = db.users.find_one(myquery)
    user_id = userDoc['_id']
    data['trusted-by-id'] = [str(user_id)]
    trusted_user_data = json.loads(json_util.dumps(data))
    
    db.trusted.insert(trusted_user_data)
    trustedUser = request.form.get("username")
    db.users.update({"username": username}, {"$push": {"trustedUser": trustedUser}})
    print("Trusted User Created")
    return True

def addTrustedUser(username, trusted_username):

    user_id = db.users.find_one({ "username": username })['_id']
    
    if(db.trusted.find({"username": trusted_username}).count() == 0):
        return False

    db.trusted.update({"username": trusted_username}, {"$push": {"trusted-by-id": str(user_id)}})
    db.users.update({"username": username}, {"$push": {"trustedUser": trusted_username}})
    return True

def getHashedUserName(trusted_username):

    myquery = { "username": trusted_username }
    trustedDoc = db.trusted.find_one(myquery)
    return trustedDoc["hashedUsername"]


def getUserUsingHash(hashedUsername):

    myquery = { "hashedUsername": hashedUsername }
    trustedDoc = db.trusted.find_one(myquery)

    if(trustedDoc == None):
        return None, None

    return trustedDoc["username"], trustedDoc["email"]


def checkIfPassIsEmpty(trusted_username):

    myquery = {"username": trusted_username}
    trustedDoc = db.trusted.find_one(myquery)

    if(trustedDoc['password'] == ''):
        return True

    return False

def TrustedUserSetPass():

    # trustedUserdoc = db.trusted.find({"username": request.form['username']})
    passvalue = getHashed(request.form['password'])
    db.trusted.update({"username": request.form['username']}, {"$set": {"password": passvalue}})
    
def getUsernameFromId(user_id):
    myquery = {'_id': ObjectId(user_id)}
    userDoc = db.users.find_one(myquery)
    return userDoc["username"]
    

def getTrustedByUsernames(trusted_user):
    myquery = { "username": trusted_user }
    trustedDoc = db.trusted.find_one(myquery)
    user_id_list = trustedDoc["trusted-by-id"]
    print(user_id_list)
    username_list = []
    for id in user_id_list:
        username_list.append(getUsernameFromId(id))
    return username_list