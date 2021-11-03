from numpy.core.fromnumeric import mean
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

# Post structure - [Date, Post, Score]

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

def get_score(post):
    return get_sentiment(post)

def addPost(user, post):
    score = get_sentiment(post)
    today = datetime.today()
    db.users.update({"username": user}, {
                    "$push": {"posts": [today, post, score]}})
    print("Post Added")

def getPost(username, limit = None):

    print("Posts retrieved")
    myquery = {"username": username}
    userDoc = db.users.find_one(myquery)

    if(userDoc == None):
        return []

    items = userDoc["posts"]

    if(limit != None):
        return items[::-1][:limit]

    return items[::-1]

def updatePost(username, new_content, id):

    userDoc = db.users.find_one({"username": username})
    length = len(userDoc['posts'])
    index = (length - int(id))

    post = userDoc["posts"][index]
    post[1] = new_content
    post[2] = get_sentiment(new_content)

    db.users.update({"username": username}, { "$set": { 'posts.'+str(index) : post}})
    return post[2]

def removePost(username, post, id):

    userDoc = db.users.find_one({"username": username})
    length = len(userDoc['posts'])
    index  = length - int(id)

    post = userDoc["posts"][index]
    db.users.update({"username": username}, {'$pull': {"posts": post}})


def getScores(username):

    myquery = {"username": username}
    userDoc = db.users.find_one(myquery)
    posts = userDoc["posts"]
    scores = []

    for entry in posts:
        scores.append(entry[2])

    return scores

def getTrustedUsers(username):
    
    userDoc = db.users.find_one({"username": username})
    unique_list = list(set(userDoc['trustedUser']))
    db.users.update({"username": username}, { "$set": { 'trustedUser' : unique_list}})

    return unique_list

def getTrustedInfo(trusted_user_list):

    info = []

    for trusted_user in trusted_user_list:
        trustedDoc = db.trusted.find_one({"username": trusted_user})
        info.append(trustedDoc)

    return info

def removeTrustedUser(username, trusted_user):

    userDoc = db.users.find_one({"username": username})
    user_id = str(userDoc['_id'])

    print(username, trusted_user, user_id)
    db.users.update({"username": username}, {'$pull': {"trustedUser": trusted_user}})
    db.trusted.update({"username": trusted_user}, {'$pull': {"trusted-by-id": user_id}})
    

def getEmailofTrustedUsers(username):

    trustedUsers = getTrustedUsers(username)

    email_list = []
    for trustedUser in trustedUsers:
        trustedDoc = db.trusted.find_one({"username": trustedUser})
        email_list.append(trustedDoc['email'])

    return email_list

def get_last_email_date(username):

    userDoc = db.users.find_one({"username": username})
    return userDoc.get('last_email')

def set_last_email_date(username):

    if(get_last_email_date(username) == None):
        db.users.update({"username": username}, {"$set": {"last_email": datetime.today()}})
    else:
        db.users.update({"username": username}, {"$set": {"last_email": datetime.today()}})
    

# def getStreak(username):
#     # All the number of consecutive days where entry exists
#     items = getPost(username)
#     for entry in items:
#         print("@@ - ")
#         print(entry)
#         print("\n")
#     return


# def currentStreak(username):
#     # Number of entries from today's date to backwards
#     return


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


def check_low_scores(username):

    posts = getPost(username, limit = 7)

    if(len(posts) == 0):
        return False
    
    mean_score = 0
    for i in range(min(len(posts), 7)):
        mean_score += posts[i][2]

    mean_score = mean_score/min(len(posts), 7)
    print("Score :", mean_score, username)
    if(mean_score < -25):
        return True

    return False