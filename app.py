from flask import Flask
from flask_ckeditor import CKEditor


app = Flask(__name__)
ckeditor = CKEditor(app)
app.jinja_env.filters['zip'] = zip
from views import *

if __name__ == "__main__":
    app.run(debug="true")