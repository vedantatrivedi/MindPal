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


def checkloginusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "No User"
    else:
        return "User exists"


def checkloginpassword():

    username = request.form["username"]
    check = db.users.find_one({"username": username})

    if(check == None):
        return "wrong"

    password = request.form["password"]
    hashpassword = getHashed(password)

    if hashpassword == check["password"]:
        session["username"] = username
        session["email"] = check["email"]
        return "correct"
    else:
        return "wrong"

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


def checkusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "Available"
    else:
        return "Username taken"


def registerUser():

    fields = [k for k in request.form]
    values = [request.form[k] for k in request.form]

    fields.append("posts")
    values.append([])

    fields.append("trusted_users")
    values.append([])

    data = dict(zip(fields, values))

    username = data['username']
    exist_count = db.users.find({"username": username}).count()

    if(exist_count > 0):
        return False
    else:
        user_data = json.loads(json_util.dumps(data))
        user_data["password"] = getHashed(user_data["password"])
        user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
        db.users.insert(user_data)
        return True


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

# Post structure - [Date, Post, Score]
def addPost(user, post):
    score = get_sentiment(post)
    today = datetime.today()
    db.users.update({"username": user}, {
                    "$push": {"posts": [today, post, score]}})
    print("Post Added")


def getPost(username):
    print("Posts retrieved")
    myquery = {"username": username}
    userDoc = db.users.find_one(myquery)

    if(userDoc == None):
        return []

    items = userDoc["posts"]
    # print(items[-1])
    return items[::-1]


def getScores(username):

    myquery = {"username": username}
    userDoc = db.users.find_one(myquery)
    posts = userDoc["posts"]
    scores = []

    for entry in posts:
        scores.append(entry[2])

    return scores

def getStreak(username):
    # All the number of consecutive days where entry exists

    return


def currentStreak(username):
    # Number of entries from today's date to backwards
    return


def getFormattedDate(date):
    return date.strftime('%b %d, %Y')


def getDayfromDate(date):
    return calendar.day_name[date.weekday()]


def getScoresForChart(username):
    scores = getScores(username)[-7:]
    return_score = np.array(scores).flatten().tolist()
    rounded_scores = [round(num) for num in return_score]
    return rounded_scores


def getScoresForPieChart(username):
    user = db.users.find_one({"username": session["username"]})
    print(session["username"])
    # print(user)
    scores = user["scores"]
    return_score = np.array(scores).flatten().tolist()
    rounded_scores = [round(num) for num in return_score]
    print(rounded_scores)
    happy_elements = [element for element in rounded_scores if element >= 90]
    med_elements = [
        element for element in rounded_scores if element >= 70 and element < 90]
    unhappy_elements = [element for element in rounded_scores if element < 70]
    happy_score = len(happy_elements)
    med_score = len(med_elements)
    unhappy_score = len(unhappy_elements)
    pie_chart_data = [happy_score, med_score, unhappy_score]
    return pie_chart_data


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

