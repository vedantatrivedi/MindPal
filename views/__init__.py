from flask import render_template, request, redirect, url_for, session, flash
from app import app
from model import *
from model import email_service
from functools import reduce
import numpy as np
from operator import add
import json

import os
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/drive.metadata.readonly"]

@app.route('/', methods=["GET"])
def home():

    if "username" in session:
        posts = getPost(session["username"])
        print("Inside home() with username " + session["username"])

        posts = getPost(session["username"])
        text, scores, dates, days = [], [], [], []

        for entry in posts:
            dates.append(getFormattedDate(entry[0]))
            text.append(entry[1])
            scores.append(entry[2])
            days.append(getDayfromDate(entry[0]))

        return render_template('index.html',username = session["username"], posts = text,scores = scores, days = days, dates = dates)
    else:
        return render_template('login.html')

# Register new user
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        response = registerUser()
        # Send Welcome Mail
        if(checkOAuthToken() and response):
            token = getOAuthToken()
            email_service.send_welcome_mail('dornumofficial@gmail.com', request.form['email'], request.form['name'], token['refresh_token'])
            return redirect(url_for("login"))
        else: 
            flash("Username already exists")
            return render_template('register.html')
    

#Check if email already exists in the registratiion page
@app.route('/checkusername', methods=["POST"])
def check():
    return checkusername()

@app.route('/addPost',methods = ["POST"])
def addPosts():

    response = {
      'status': 400,
    }

    try:
        addPost(session['username'], request.form['ckeditor'])
        response = {
          'status': 201,
        }

    except:
        pass

    return redirect('/')
    
@app.route('/getPosts', methods = ["Get"])
def getPosts():
    
    response = {
      'status': 400,
      'body'  : '',
    }

    try:
        response = {
          'status': 200,
          'body'  : json.dumps(getPost(session["username"])),
        }
    except:
        pass
    

    return response



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
@app.route('/add-trusted-user', methods=["GET","POST"])
def addtrusted():
    
    if request.method == "GET":
        return render_template("add_trusted_user.html")
    elif request.method == "POST":
        addTrustedUser(session["username"])
        return render_template('index.html',username = session["username"], 
             posts = getPost(session["username"]),scores = getScores(session["username"]), dates=getDates(session["username"]))

#utilities-other
@app.route('/utilities-other', methods=["GET"])
def utilitiesother():
    return render_template("utilities-other.html")


# @app.route('/send_mail', methods=["GET"])

# def send_mail():
#     email_service.send_mail('dornumofficial@gmail.com', 'dornumofficial@gmail.com',
#               'A mail from you from Python',
#               '<b>A mail from you from Python</b><br>', session['credentials']['refresh_token'])

#     return ""


@app.route('/authorize', methods=["GET"])
def authorize():

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    if(checkOAuthToken()):
        return redirect('/')
    else:
        session['state'] = state
    
    return redirect(authorization_url)

@app.route('/oauth2callback', methods=["GET","POST"])
def oauth2callback():

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response = authorization_response)


    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.

    credentials = credentials_to_dict(flow.credentials)
    putOAuthToken(credentials)

    return redirect('/')

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}