"""
Flask server
"""


from flask import Flask, render_template
from flask_cors import CORS

from cardboard.blueprints import cardboard_blueprint
from cardboard import cardboard


app = Flask(__name__)
cors = CORS(app, origins=['*', 'http://localhost:5173', "http://127.0.0.1:5173"])

cardboard_blueprint.static_folder = "./dist"
app.register_blueprint(cardboard_blueprint)

# Load the board configuration
with open("./tests/data/cards.json") as f:
    import json
    board_json = json.load(f)
    cardboard.configure_board(data=board_json)


if __name__ == '__main__': 
    app.run(host="127.0.0.1", port=5000, debug=True)

