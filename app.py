from flask import Flask
from flask_ckeditor import CKEditor
import ssl
# from waitress import serve

app = Flask(__name__)
ckeditor = CKEditor(app)
app.jinja_env.filters['zip'] = zip

from views import *

if __name__ == "__main__":
    context = ssl.SSLContext()
    context.load_cert_chain('server.crt', 'server.key')
    # serve(app, host="127.0.0.1", port=500)
    app.run(ssl_context = context, debug="true")