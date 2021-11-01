from flask import render_template, request, redirect, url_for, session, flash
from app import app
from model import email_service, trusted_users, oauth, users
from datetime import datetime, timedelta
import json
import google_auth_oauthlib.flow
import threading

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]


@app.route('/', methods=["GET"])
def home():
    if "username" in session:

        trusted_users = users.getTrustedUsers(session['username'])

        # Checking if last 7 entries have low score and last mail sent greater than 15 days
        check_low = users.check_low_scores(session['username'])
        if(check_low == True):

            last_email_date = users.get_last_email_date(session['username'])
            if(last_email_date == None or ( (datetime.today() - last_email_date).days >= 15) ):

                if(oauth.checkOAuthToken()):
                    token = oauth.getOAuthToken()
                    trusted_users_emails = (users.getEmailofTrustedUsers(session['username']))
                    send_mail_thread = threading.Thread(target=email_service.send_welcome_mail, args=('dornumofficial@gmail.com', 'dornumofficial@gmail.com', session['username'], token['refresh_token'],))
                    send_mail_thread.start()
                    users.set_last_email_date(session['username'])



        return render_template('index.html', username=session["username"], trusted_users=trusted_users)
    
    else:

        return render_template('home-page.html')

# Register new user
@app.route('/register', methods=["GET", "POST"])
def register():
    
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":

        response = users.registerUser()

        # Sending Welcome Mail
        if(oauth.checkOAuthToken() and response):
            
            token = oauth.getOAuthToken()
            send_mail_thread = threading.Thread(target=email_service.send_welcome_mail, args=('dornumofficial@gmail.com', request.form['email'], request.form['name'], token['refresh_token'],))
            send_mail_thread.start()

            return redirect(url_for("login"))
        else:

            flash("Username already exists")
            return render_template('register.html')


# Check if email already exists in the registratiion page
@app.route('/checkusername', methods=["POST"])
def check():
    return users.checkusername()


@app.route('/addPost', methods=["POST"])
def addPosts():

    text = request.form['ckeditor']
    add_post_thread = threading.Thread(target=users.addPost, args=(session['username'], text,))
    add_post_thread.start()

    session['posts'].insert(0, [datetime.today(), text, 0])
    session.modified = True

    print("HDHSH", session['posts'])
    return redirect(url_for("Posts"))


@app.route('/getPosts', methods=["Get"])
def getPosts():

    response = {
        'status': 400,
        'body': '',
    }

    try:
        response = {
            'status': 200,
            'body': json.dumps(users.getPost(session["username"])),
        }
    except:
        pass

    return response

@app.route('/posts', methods=["Get"])
def Posts():

    if('posts' not in session):
        posts = users.getPost(session["username"])
        session['posts'] = posts
    else:
        posts = session['posts']

    text, scores, dates, days = [], [], [], []

    for entry in posts:
        dates.append(users.getFormattedDate(entry[0]))
        text.append(entry[1])
        scores.append(entry[2])
        days.append(users.getDayfromDate(entry[0]))


    return render_template('posts.html', username = session["username"], posts = text, scores = scores, days = days, dates = dates)

# Everything Login (Routes to renderpage, check if username exist and also verifypassword through Jquery AJAX request)
@app.route('/login', methods=["GET"])
def login():
    if request.method == "GET":
        if "username" not in session:
            return render_template("login.html")
        else:
            return redirect(url_for("home"))


@app.route('/trusted_user_login', methods=["GET", "POST"])
def trusted_user_login():
    if request.method == "GET":
        if "trusted_users" not in session:
            return render_template("trusted_user_login.html")
        else:
            return redirect('/trusted_user_dashboard')
        

@app.route('/trusted_user_dashboard', methods=["GET"])
def trustedHome():
    if "trusted_users" in session:
        trusted_username = session["trusted_users"]
        print(trusted_username)
        trusted_by_list = trusted_users.getTrustedByUsernames(trusted_username)
        data = trusted_users.getTrustedByChartData(trusted_username)
        scores = []
        for user in trusted_by_list:
            scores.append(users.getScoresForChart(user))
        labels = ["Monday", "Tuesday", "Wednesday",
                  "Thursday", "Friday", "Saturday", "Sunday"]
        return render_template("trustedUserDashboard.html", data = data, scores=scores, labels=labels,user_list = trusted_by_list)
    else:
        return render_template("trusted_user_login.html")
        
    
@app.route('/checkloginusername', methods=["POST"])
def check_user_login():
    return users.checkusername()


@app.route('/checkloginpassword', methods=["POST"])
def checkUserpassword():
    return users.checkloginpassword()

@app.route('/checkTrustedUsername', methods=["POST"])
def checkTrusted_user_login():
    return trusted_users.checkTrustedUsername()


@app.route('/checkTrustedPassword', methods=["POST"])
def checkTrustedpassword():
    return trusted_users.checkTrustedPassword()

# The admin logout
@app.route('/logout', methods=["GET"])  # URL for logout
def logout():  # logout function
    session.clear()
    return redirect(url_for("home"))  # redirect to home page with message

@app.route('/TrustedUserLogout', methods=["GET"])  # URL for logout
def TrustedUserLogout():  # logout function
    session.pop('trusted_users', None)  # remove user session
    return redirect(url_for("home"))  # redirect to home page with message

# Forgot Password
@app.route('/forgot-password', methods=["GET"])
def forgotpassword():
    return render_template('forgot-password.html')

# 404 Page
@app.route('/404', methods=["GET"])
def errorpage():
    return render_template("404.html")

# Blank Page
@app.route('/blank', methods=["GET"])
def blank():
    return render_template('blank.html')

# Buttons Page
@app.route('/buttons', methods=["GET"])
def buttons():
    return render_template("buttons.html")

# Cards Page
@app.route('/cards', methods=["GET"])
def cards():
    return render_template('cards.html')

# Charts Page
@app.route('/charts', methods=["GET"])
def charts():
    scores = users.getScoresForChart(session["username"])
    labels = ["Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday", "Sunday"]
    return render_template("charts.html", scores=scores, labels=labels, user=session["username"])

# Tables Page
@app.route('/tables', methods=["GET"])
def tables():
    return render_template("tables.html")

# Utilities-animation
@app.route('/utilities-animation', methods=["GET"])
def utilitiesanimation():
    return render_template("utilities-animation.html")

# Utilities-border
@app.route('/utilities-border', methods=["GET", "POST"])
def utilitiesborder():
    return render_template("utilities-border.html")

#Utilities-color
@app.route('/add-trusted-user', methods=["GET","POST"])
def addtrusted():
    
    if request.method == "GET":
        return render_template("add_trusted_user.html")

    elif request.method == "POST":

        # Trusted user with existing username
        if(request.form["button"] == "Same User"):

            response = trusted_users.addTrustedUser(session["username"], (request.form['username']))

            # Adding to existing trusted user
            if(response == True):
                return redirect(url_for("home")) 

            # username was changed but clicked wrong button
            else:

                flash('Please create a new Trusted user')
                return render_template('add_trusted_user.html')

        response = trusted_users.createTrustedUser(session["username"])

        # Trusted user with same username exists, so providing option to add this user or create new
        if(response != True):
            flash('Username already exists with email ' + response)
            return render_template('add_trusted_user.html', showButton = True, user = request.form['username'], name = request.form['name'], mail = response)
        
        # Creating new trusted User, sending mail for setting password
        if(oauth.checkOAuthToken()):

            hashedUsername = trusted_users.getHashedUserName(request.form['username'])
            token = oauth.getOAuthToken()
            link = request.url_root + 'set_password?user=' + hashedUsername

            send_mail_thread = threading.Thread(target=email_service.send_set_pass_mail, args=('dornumofficial@gmail.com', request.form['email'], request.form['username'], session["username"], link, token['refresh_token']))
            send_mail_thread.start()

        return redirect(url_for("home"))

# Testing endpoint for sending mail 
@app.route('/send_mail', methods=["GET"])
def send_mail():
    token = oauth.getOAuthToken()
    send_mail_thread = threading.Thread(target=email_service.send_welcome_mail, args=('dornumofficial@gmail.com', 'dornumofficial@gmail.com', "SA", token['refresh_token']))
    send_mail_thread.start()
    return redirect(url_for("home"))

@app.route( '/currentStreak', methods=[ "Get" ] )
def currentStreak():

    curStreak = 0
    curTime = -1

    for post in users.getPost( session[ "username" ] ):
        if curTime == -1:
            curTime = post[0]
            curStreak += 1

        elif ( curTime - post[0] ).days >= 1 and ( curTime - post[0] ).days < 2:
            curStreak += 1
            curTime = post[0]

        elif ( curTime - post[0] ).days < 1:
            curTime = post[0]
            continue

        else:
            break

    response = {
        'status': 200,
        'body': curStreak,
    }
    return response

@app.route( '/maxStreak', methods = [ "Get" ] )
def maxStreak( ):
    curStreak = 0
    maxStreak = 0
    curTime = -1

    for post in users.getPost(session["username"]):
        # print (post[0])
        if curTime == -1:
            curTime = post[0]
            curStreak += 1

        elif (curTime - post[0]).days >= 1 and (curTime - post[0]).days < 2:
            print(curTime, post[0])
            curStreak += 1
            curTime = post[0]

        elif ( curTime - post[0] ).days < 1:
            curTime = post[0]
            continue
        else:
            if curStreak > maxStreak:
                maxStreak = curStreak
            curStreak = 1
            curTime = post[0]

    if curStreak > maxStreak:
        maxStreak = curStreak

    response = {
        'status': 200,
        'body': maxStreak,
    }
    return response

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

    if(oauth.checkOAuthToken()):
        return redirect('/')
    else:
        session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback', methods=["GET", "POST"])
def oauth2callback():

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = credentials_to_dict(flow.credentials)
    oauth.putOAuthToken(credentials)

    return redirect('/')

@app.route('/set_password', methods=["GET", "POST"])
def set_password():

    if request.method == "GET":

        hashedUsername = request.args.get('user')
        if(hashedUsername == None):
            return redirect(url_for("errorpage"))

        username, email = trusted_users.getUserUsingHash(hashedUsername)

        if(trusted_users.checkIfPassIsEmpty(username) == False or username == None):
            return redirect(url_for("errorpage"))

        return render_template("trusted_user_set_password.html", username = username, email = email)

    elif request.method == "POST":

        trusted_users.TrustedUserSetPass()
        return redirect(url_for("login"))

@app.route('/getEntries',methods = ["GET"])
def getEntries():
    return json.dumps(users.getPost(session["username"]),indent=4, sort_keys=True, default=str)

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
