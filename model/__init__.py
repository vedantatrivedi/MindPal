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
import re

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
    password = request.form["password"]
    hashpassword = getHashed(password)
    if hashpassword == check["password"]:
        session["username"] = username
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
    fields.append("scores")
    values.append([])
    fields.append("date")
    values.append([])
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert(user_data)
    print("Done")

def addTrustedUser(username):
    fields = [k for k in request.form]                                      
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    fields.append("users")
    values.append(username)
    db.trusted.insert(user_data)
    trustedUser = request.form.get("username")
    db.users.update({"username": username}, {"$push": {"trustedUser": trustedUser}})
    print("Done")
    

def addPost(user,post):
    print(post)
    score = get_score(post)
    today = datetime.today()
    db.users.update({"username": user}, {"$push": {"posts": [post],"scores":[score],"date":[today]}})
    print("Post Added")

def getPost(username):
    print("Posts retrieved")
    myquery = { "username": username }
    userDoc = db.users.find_one(myquery)
    items=userDoc["posts"]
    # print(items[-1])
    return items

def getScores(username):
    print("Posts retrieved")
    myquery = { "username": username }
    userDoc = db.users.find_one(myquery)
    scores=userDoc["scores"]
    return scores

def getDates(username):
    print("Dates Retrieved")
    myquery = { "username": username }
    userDoc = db.users.find_one(myquery)
    dates = userDoc["date"]
    days=[]
    formatted_dates=[]
    for i in dates:
        days.append(calendar.day_name[i[0].weekday()])
        # temp = i[0].day+ ' / '+i[0].month+' / '+[0].year
        formatted_dates.append(i[0].strftime('%b %d, %Y'))
    return formatted_dates

def getDays(username):
    print("Days Retrieved")
    myquery = { "username": username }
    userDoc = db.users.find_one(myquery)
    dates = userDoc["date"]
    days=[]
    for i in dates:
        days.append(calendar.day_name[i[0].weekday()])
       
    return days


    
def getScoresForChart(username):
    user = db.users.find_one({"username":username})
    # print(session["username"])
    # print(user)
    scores = user["scores"]
    return_score = np.array(scores).flatten().tolist()
    rounded_scores = [round(num) for num in return_score]
    print(rounded_scores)
    return rounded_scores[-7:]

def getScoresForPieChart(username):
    user = db.users.find_one({"username":session["username"]})
    print(session["username"])
    # print(user)
    scores = user["scores"]
    return_score = np.array(scores).flatten().tolist()
    rounded_scores = [round(num) for num in return_score]
    print(rounded_scores)
    happy_elements = [element for element in rounded_scores if element >= 90]
    med_elements = [element for element in rounded_scores if element >= 70 and element < 90]
    unhappy_elements = [element for element in rounded_scores if element < 70]
    happy_score = len(happy_elements)
    med_score = len(med_elements)
    unhappy_score = len(unhappy_elements)
    pie_chart_data = [happy_score,med_score,unhappy_score]
    return pie_chart_data