from flask import Flask
import flask_cors

from .manager import Manager
from .apis.v2 import V2

def run():
  app = Flask(__name__)
  flask_cors.CORS(app)

  V2(Manager(), app)
  
  app.run(host="0.0.0.0", port=80, use_reloader=False, threaded=True, debug=False)