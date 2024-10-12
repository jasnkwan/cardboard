"""
Flask server
"""


from flask import Flask
from flask_cors import CORS

from cardboard.cardboard import cardboard_blueprint


app = Flask(__name__)
cors = CORS(app, origins=['*', 'http://localhost:5173', "http://127.0.0.1:5173"])

app.register_blueprint(cardboard_blueprint)



if __name__ == '__main__': 
    app.run(host="127.0.0.1", port=5000, debug=True)
    #cardboard.shutdown()
