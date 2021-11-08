from flask import render_template, request, redirect, url_for, session, flash
from app import app
from model import email_service, trusted_users, oauth, users
from datetime import  datetime
import json, os
import google_auth_oauthlib.flow
import threading

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

app.secret_key = "ITSASECRET"

@app.route('/', methods=["GET"])
def home():
    if "username" in session:

        trusted_users = users.getTrustedUsers(session['username'])

        # Checking if last 15 entries have low score and last mail sent greater than 15 days
        check_low = users.check_low_scores(session['username'])
        if(check_low == True):

            last_email_date = users.get_last_email_date(session['username'])
            if(last_email_date == None or ( (datetime.today() - last_email_date).days >= 15) ):

                if(oauth.checkOAuthToken()):
                    token = oauth.getOAuthToken()
                    trusted_users_emails = (users.getEmailofTrustedUsers(session['username']))
                    send_mail_thread = threading.Thread(target=email_service.send_welcome_mail, args=('dornumofficial@gmail.com', 'dornumofficial@gmail.com', session['username'], token['refresh_token'], request.url_root))
                    send_mail_thread.start()
                    users.set_last_email_date(session['username'])

            # TODO : send Report if low score in last 15 days


        return render_template('index.html', username=session["username"], trusted_users=trusted_users, currStreak = users.getCurrentStreak(session['username']),maxStreak = users.getMaxStreak(session['username']))
    
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
            send_mail_thread = threading.Thread(target=email_service.send_welcome_mail, args=('dornumofficial@gmail.com', request.form['email'], request.form['name'], token['refresh_token'], request.url_root))
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

    if('username' not in session):
        return redirect(url_for("home"))

    text = request.form['ckeditor']
    add_post_thread = threading.Thread(target=users.addPost, args=(session['username'], text,))
    add_post_thread.start()

    session['posts'].insert(0, [datetime.today(), text, users.get_score(text)])
    session.modified = True

    return redirect(url_for("Posts"))

# Get posts for a user
@app.route('/getPosts', methods=["GET"])
def getPosts():

    if('username' not in session):
        return redirect(url_for("home"))

    return json.dumps(users.getPost(session["username"]),indent=4, sort_keys=True, default=str)


# Update posts for a user
@app.route('/updatePosts', methods=["GET"])
def updatePosts():

    if('username' not in session):
        return redirect(url_for("home"))

    content = request.args.get('content')
    id = request.args.get('id')
    new_score = users.updatePost(session['username'], content, id)

    new_entry = [datetime.now(), content, new_score]
    session['posts'][int(id)-1] = new_entry
    session.modified = True

    return "200"

@app.route('/deletePost', methods=["GET"])
def deletePost():

    if('username' not in session):
        return redirect(url_for("home"))

    id = request.args.get('id')

    post = session['posts'][int(id)-1]
    users.removePost(session['username'], post, id)

    session['posts'].pop(int(id)-1)
    session.modified = True

    return "200"

# Endpoint for posts page 
@app.route('/posts', methods=["GET"])
def Posts():

    if('username' not in session):
        return redirect(url_for("home"))

    if('posts' not in session):
        posts = users.getPost(session["username"])
        session['posts'] = posts
    else:
        posts = session['posts']

    text, scores, dates, days, allow_edits = [], [], [], [], []

    for entry in posts:
        dates.append(users.getFormattedDate(entry[0]))
        text.append(entry[1])
        scores.append(entry[2])
        days.append(users.getDayfromDate(entry[0]))
        allow_edits.append( (datetime.today()-entry[0].replace(tzinfo=None)).days < 1)

    return render_template('posts.html', username = session["username"], posts = text, scores = scores, days = days, dates = dates, allow_edits = allow_edits)

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
            session.clear()
            return redirect('/trusted_user_dashboard')
        

@app.route('/trusted_user_dashboard', methods=["GET"])
def trustedHome():
    
    if "trusted_users" in session:
        
        trusted_username = session["trusted_users"]
        trusted_by_list = trusted_users.getTrustedByUsernames(trusted_username)
        
        scores, last_post, num_posts, streak, labels = [], [], [], [], []

        for user in trusted_by_list:

            scores_list = users.getScoresForChart(user)
            scores.append(scores_list[0])
            labels.append(scores_list[1])

            posts = users.getPost(user)
            last_post.append(users.getFormattedDate(posts[0][0]))
            num_posts.append(len(posts))
            streak.append(users.getCurrentStreak(user))

        return render_template("trustedUserDashboard.html", scores = scores, labels = labels, user_list = trusted_by_list, username = session["trusted_users"], last_post = last_post, num_posts = num_posts, streak = streak)
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

# Charts Page
@app.route('/charts', methods=["GET"])
def charts():
    scores, labels = users.getScoresForChart(session["username"])
    # labels = ["Monday", "Tuesday", "Wednesday",
    #           "Thursday", "Friday", "Saturday", "Sunday"]
    emotion_labels = ["Sadness", "Joy","Fear","Disgust", "Anger"]
    emotions = users.getPieChartData(session["username"])
    emotion_percentages = list(emotions.values())
    print(emotion_percentages)
    return render_template("charts.html", pieChartLabels = emotion_labels,emotions = emotion_percentages,scores=scores, labels=labels, user=session["username"])

# Adding a trusted user
@app.route('/trusted-user', methods=["GET","POST"])
def trustedUser():

    if "username" not in session:
        return redirect(url_for("home"))


    if request.method == "GET":

        trusted_user = users.getTrustedUsers(session['username'])
        trusted_users_info = users.getTrustedInfo(trusted_user)
        return render_template("trusted_user.html", trusted_users = trusted_users_info)

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
                return render_template('trusted_user.html')

        response = trusted_users.createTrustedUser(session["username"])

        # Trusted user with same username exists, so providing option to add this user or create new
        if(response != True):
            flash('Username already exists with email ' + response)
            return render_template('trusted_user.html', showButton = True, user = request.form['username'], name = request.form['name'], mail = response)
        
        # Creating new trusted User, sending mail for setting password
        if(oauth.checkOAuthToken()):

            hashedUsername = trusted_users.getHashedUserName(request.form['username'])
            token = oauth.getOAuthToken()
            link = request.url_root + 'set_password?user=' + hashedUsername

            send_mail_thread = threading.Thread(target=email_service.send_set_pass_mail, args=('dornumofficial@gmail.com', request.form['email'], request.form['username'], session["username"], link, token['refresh_token']))
            send_mail_thread.start()

        return redirect(url_for("trustedUser"))

@app.route('/deleteTrustedUser', methods=["GET"])
def deleteTrustedUser():

    if('username' not in session):
        return redirect(url_for("home"))

    users.removeTrustedUser(session['username'], request.args.get('name'))    
    return "200"

@app.route('/resendMail', methods=["GET"])
def resendMail():

    if('username' not in session):
        return redirect(url_for("home"))

    if(oauth.checkOAuthToken()):

        hashedUsername = trusted_users.getHashedUserName(request.args.get('name'))
        token = oauth.getOAuthToken()
        link = request.url_root + 'set_password?user=' + hashedUsername

        send_mail_thread = threading.Thread(target=email_service.send_set_pass_mail, args=('dornumofficial@gmail.com', request.args.get('email'), request.args.get('name'), session["username"], link, token['refresh_token']))
        send_mail_thread.start()

    return "200"


# @app.route( '/currentStreak', methods=[ "GET" ] )
# def currentStreak():

#     curStreak = 0
#     curTime = -1

#     for post in users.getPost( session[ "username" ] ):
#         if curTime == -1:
#             curTime = post[0]
#             curStreak += 1

#         elif ( curTime - post[0] ).days >= 1 and ( curTime - post[0] ).days < 2:
#             curStreak += 1
#             curTime = post[0]

#         elif ( curTime - post[0] ).days < 1:
#             curTime = post[0]
#             continue

#         else:
#             break

#     response = {
#         'status': 200,
#         'body': curStreak,
#     }
#     return response

# @app.route( '/maxStreak', methods = [ "GET" ] )
# def maxStreak( ):
#     curStreak = 0
#     maxStreak = 0
#     curTime = -1

#     for post in users.getPost(session["username"]):
#         # print (post[0])
#         if curTime == -1:
#             curTime = post[0]
#             curStreak += 1

#         elif (curTime - post[0]).days >= 1 and (curTime - post[0]).days < 2:
#             print(curTime, post[0])
#             curStreak += 1
#             curTime = post[0]

#         elif ( curTime - post[0] ).days < 1:
#             curTime = post[0]
#             continue
#         else:
#             if curStreak > maxStreak:
#                 maxStreak = curStreak
#             curStreak = 1
#             curTime = post[0]

#     if curStreak > maxStreak:
#         maxStreak = curStreak

#     response = {
#         'status': 200,
#         'body': maxStreak,
#     }
#     return response

@app.route('/calendar', methods=["GET"])
def calendar():
    if "username" in session:
        return render_template('calendar.html', username=session["username"], currStreak = users.getCurrentStreak(session['username']),maxStreak = users.getMaxStreak(session['username']))
    else:
        return render_template('home-page.html')

@app.route('/exercises', methods=["GET"])
def exercises():
    if "username" in session:
        return render_template('exercises.html')
    else:
        return render_template('home-page.html')


@app.route('/authorize', methods=["GET"])
def authorize():

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(client_config=json.loads(os.environ['CLIENT_SECRETS']), scopes=SCOPES)

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
    flow = google_auth_oauthlib.flow.Flow.from_client_config(client_config=json.loads(os.environ['CLIENT_SECRETS']), scopes = SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = oauth.credentials_to_dict(flow.credentials)
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

        session.clear()
        trusted_users.TrustedUserSetPass()
        return redirect(url_for("trustedUser"))



