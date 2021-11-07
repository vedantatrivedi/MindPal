from numpy.core.fromnumeric import mean
from app import app
from flask import request, session
from helpers.database import *
from helpers.hashpass import *
from helpers.nlp import *
from bson import json_util, ObjectId
from datetime import datetime, timedelta
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
    scores, dates = [], []

    for entry in posts:
        scores.append(entry[2])
        dates.append(getFormattedDate(entry[0]))

    return scores, dates

def getTrustedUsers(username):
    
    userDoc = db.users.find_one({"username": username})
    trusted_users = userDoc.get('trustedUser')
    if(trusted_users == None):
        return []
    
    unique_list = list(set(userDoc.get('trustedUser')))
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
    
def getMaxStreak(username):

    curStreak, maxStreak, curTime = 0, 0, -1
    posts = getPost(username)

    dates = []
    for post in posts:
        dates.append(post[0].date())

    dates = sorted(list(set(dates)),reverse=True)

    for date in dates:

        if curTime == -1:
            curTime = date
            curStreak += 1

        elif (curTime == date):
            curStreak += 1

        else:
            currStreak = 1
            maxStreak = max(maxStreak, curStreak)
            curTime = date
            # continue

        curTime = curTime - timedelta(days = 1)
        print(curStreak, maxStreak, curTime, date)

    if curStreak > maxStreak:
        maxStreak = curStreak

    return maxStreak

def getCurrentStreak(username):
    
    curStreak, curTime = 0, -1
    posts = getPost(username)

    dates = []
    for post in posts:
        dates.append(post[0].date())

    dates = sorted(list(set(dates)),reverse=True)

    for date in dates:

        if curTime == -1:
            curTime = date
            curStreak += 1

        elif (curTime == date):
            curStreak += 1

        else:
            break

        curTime = curTime - timedelta(days = 1)
        
    return curStreak


def getFormattedDate(date):
    return date.strftime('%b %d, %Y')


def getDayfromDate(date):
    return calendar.day_name[date.weekday()]


def getScoresForChart(username):
    scores, dates = getScores(username)[-15:]
    return_score = np.array(scores).flatten().tolist()
    rounded_scores = [round(num) for num in return_score]
    return rounded_scores, dates


def getPieChartData(username):
    
    posts = getPost(username,limit = 15)
    
    if(len(posts) == 0):
        return {"Sadness": 20, "Joy": 20, "Fear":20, "Disgust": 20, "Anger": 20}
    
    emotions_list = ['sadness', 'joy', 'fear', 'disgust', 'anger']
    dic = {}

    for emotion in emotions_list:
        dic[emotion] = 0

    for post in posts:
        emotions = get_emotions(post[1])
        doc = json.loads(emotions)

        for emotion in emotions_list:
            dic[emotion] = dic[emotion] + doc[emotion]

    total = 0
    for emotion in emotions_list:
        total += dic[emotion]

    print(total, dic)
    if(total == 0):
        return {"Sadness": 20, "Joy": 20, "Fear":20, "Disgust": 20, "Anger": 20}

    for emotion in emotions_list:
        dic[emotion] = 100 * (dic[emotion] / total)

    return_data = {"Sadness": dic['sadness'], "Joy": dic['joy'], "Fear": dic['fear'], "Disgust": dic['disgust'],"Anger": dic['anger'] }
    return return_data


def check_low_scores(username):

    posts = getPost(username, limit = 15)

    if(len(posts) == 0):
        return False
    
    mean_score = 0
    for i in range(min(len(posts), 15)):
        mean_score += posts[i][2]

    mean_score = mean_score/min(len(posts), 15)
    print("Score :", mean_score, username)
    if(mean_score < -25):
        return True

    return False