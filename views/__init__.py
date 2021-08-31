from flask import render_template, request, redirect, url_for, session
from app import app
from model import *
from functools import reduce
import numpy as np
from operator import add

@app.route('/', methods=["GET","POST"])
def home():
    if request.method == "GET":
         if "username" in session:
            #  posts = getPost(session["username"])
             print("Inside home() with username " + session["username"])
            #  print(posts)
             return render_template('index.html',username = session["username"], 
             posts = getPost(session["username"]),scores = getScores(session["username"]), days=getDays(session["username"]), dates=getDates(session["username"]))
         else:
            return render_template('login.html')
    else:
        content = request.form.get("ckeditor")
        addPost(session["username"],content)
        getPost(session["username"])
        print(getPost(session["username"]))
        return render_template('index.html',username = session["username"], 
             posts = getPost(session["username"]),scores = getScores(session["username"]), dates=getDates(session["username"]))

# Register new user
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        registerUser()
        return redirect(url_for("login"))
    


#Check if email already exists in the registratiion page
@app.route('/checkusername', methods=["POST"])
def check():
    return checkusername()

@app.route('/addPost',methods = ["POST"])
def addPosts():
    return addPost()

# @app.route('/getPosts',methods = ["GET"])
# def getPosts():
#     return getPost(session["username"])

# Everything Login (Routes to renderpage, check if username exist and also verifypassword through Jquery AJAX request)
@app.route('/login', methods=["GET"])
def login():
    if request.method == "GET":
        if "username" not in session:
            return render_template("login.html")
        else:
            return redirect(url_for("home"))

@app.route('/userlogin', methods=["GET","POST"])
def userlogin():
    if request.method == "GET":
        return render_template("userlogin.html")
    else:
        scores = getScoresForChart("test")
        labels= ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        return render_template("trustedUserDashboard.html",scores = scores,labels = labels)




@app.route('/checkloginusername', methods=["POST"])
def checkUserlogin():
    return checkloginusername()

@app.route('/checkloginpassword', methods=["POST"])
def checkUserpassword():
    return checkloginpassword()

#The admin logout
@app.route('/logout', methods=["GET"])  # URL for logout
def logout():  # logout function
    session.pop('username', None)  # remove user session
    return redirect(url_for("home"))  # redirect to home page with message

#Forgot Password
@app.route('/forgot-password', methods=["GET"])
def forgotpassword():
    return render_template('forgot-password.html')

#404 Page
@app.route('/404', methods=["GET"])
def errorpage():
    return render_template("404.html")

#Blank Page
@app.route('/blank', methods=["GET"])
def blank():
    return render_template('blank.html')

#Buttons Page
@app.route('/buttons', methods=["GET"])
def buttons():
    return render_template("buttons.html")

#Cards Page
@app.route('/cards', methods=["GET"])
def cards():
    return render_template('cards.html')

#Charts Page
@app.route('/charts', methods=["GET"])
def charts():
    scores = getScoresForChart(session["username"])
    labels= ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    return render_template("charts.html",scores = scores,labels = labels,user=session["username"])

#Tables Page
@app.route('/tables', methods=["GET"])
def tables():
    return render_template("tables.html")

#Utilities-animation
@app.route('/utilities-animation', methods=["GET"])
def utilitiesanimation():
    return render_template("utilities-animation.html")

#Utilities-border
@app.route('/utilities-border', methods=["GET","POST"])
def utilitiesborder():
    return render_template("utilities-border.html")

#Utilities-color
@app.route('/utilities-color', methods=["GET","POST"])
def utilitiescolor():
    
    if request.method == "GET":
        return render_template("utilities-color.html")
    elif request.method == "POST":
        addTrustedUser(session["username"])
        return render_template('index.html',username = session["username"], 
             posts = getPost(session["username"]),scores = getScores(session["username"]), dates=getDates(session["username"]))

#utilities-other
@app.route('/utilities-other', methods=["GET"])
def utilitiesother():
    return render_template("utilities-other.html")


