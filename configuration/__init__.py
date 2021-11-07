from app import app
import urllib

# secret key for user session
app.secret_key = "90129wq#@#}{_)_+EWW}E{EW{E19001209uufdjdbf@@!!FDFDFDFSQQ@!@"

#setting up mail
app.config['MAIL_SERVER']='' #mail server
app.config['MAIL_PORT'] = 587 #mail port
app.config['MAIL_USERNAME'] = '' #email
app.config['MAIL_USE_TLS'] = True #security type
app.config['MAIL_USE_SSL'] = False #security type


