  
<h1 align="center">
  <br>
  <a href="https://mindpal.herokuapp.com/"><img src="https://i.ibb.co/4R22KF4/Mind-Pal-Logo.png" alt="Mind-Pal-Logo" width = "300"></a>
  <br>
  MindPal
</h1>
<p align = "center">
<a href="https://mindpal.herokuapp.com/">
    <img src="https://img.shields.io/badge/-View Live-green.svg"
         alt="mindpal.herokuapp.com">
  </a>
  </p>
<h4 align="center">Journal your thoughts, track your emotions and keep your loved ones updated.</h4>

<p align="center">
  <a href="https://www.hackerearth.com/challenges/hackathon/reimaginefuture-hackathon/">
    <img src="https://img.shields.io/badge/IBM-Reimagine <Future> Hackathon-orange.svg"
         alt="IBM Reimagine Future Hackathon">
  </a>
  
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#tools--technologies">Tools and Technologies</a> •
  <a href="#Contributors">Contributors</a> 
</p>

![screenshot](https://i.ibb.co/rZQKYP4/MindPal.gif)

## Key Features

* Full-featured Javascript text editor.
  - Allows you to type your journal entries or transcribes your speech using our voice2text feature.
* Smart Insights on your entries.
	* We use [IBM Watson Natural Language Understanding](https://www.ibm.com/in-en/cloud/watson-natural-language-understanding) to extract the emotions and the sentiment of journal entries, allowing them to understand their thoughts and emotions better.
	* The scores are visualised in a dashboard allowing you to easily understand patterns in your mental health.
* Trusted Users
  - Keep your loved ones updated on your mental health by allowing them to see your visualised scores from your entries - keeping them stress free :)
* Mailing System
	* Add trusted users seamlessly by entering their name, username and email id on your account - they will receive an email from us to set their password, and they can get started right away!
	* It can be difficult to communicate when we feel low - which is why we send an email to your trusted users when your emotional scores are consistently low. Letting them know decreases the communication gap, and also improves relationships.
* Calendar 
	* Maintain consistency and easily navigate through your posts using our calendar based visualisation - allowing you to view all entries from a day with just one click.
* Mental Health Exercises
	* We include a guide to Grounding Exercises for those unfortunate moments of anxiety and give you a list of activities to do when you feel low, to make sure that you are well in the troughs.

## Services to setup
The deployed version <a href="https://mindpal.herokuapp.com/">link</a> has everything setup and is fully functional. 

For personal use, the following services need to be set up. Variables like connection string and client ID are added as environment variables for security purposes. The variables are used in views/__init.py, model/email_service.py, helpers/nlp.py, and helpers/database.py.

1. Google OAuth for Email
2. MongoDB
3. IBM NLP
## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python 3 or above](https://www.python.org/downloads/) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/vedantatrivedi/MindPal.git

# Go into the repository
$ cd MindPal

# (Recommended but optional) Make a virtual enviroment and activate it
$ python3 -m pip install --user virtualenv 
$ python3 -m venv env
$ source env/bin/activate

# Install dependencies
$ pip3 install -r requirements.txt

# Run the app
$ python3 app.py
```
## Tools / Technologies


- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Bootstrap](https://getbootstrap.com/)
- [CKEditor](https://ckeditor.com/)
- [Calendar.js](https://fullcalendar.io/)
-  [Chartjs](https://www.chartjs.org/)
- [MongoDB](https://www.mongodb.com/)


## Contributors

- [Vedanta Trivedi](https://github.com/vedantatrivedi) 
- [Jinit Shah](https://github.com/jinit24) 
- [Mansi Parashar](https://github.com/mansiparashar00)
- [Syed Mujtaba Jafri](https://github.com/mujtaba1747)

