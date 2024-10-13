from flask import Blueprint, jsonify, send_from_directory, render_template, current_app, request
from cardboard.cardboard import start_card, stop_card
from cardboard import cardboard
import importlib.resources as pkg_resources
import os

# Load environment variables
CARDBOARD_FLASK_HOST = os.environ.get("CARDBOARD_FLASK_HOST", default="127.0.0.1")
CARDBOARD_FLASK_PORT = int(os.environ.get("CARDBOARD_FLASK_PORT", default="5000"))
CARDBOARD_STATIC_DIR = os.environ.get("CARDBOARD_STATIC_DIR", default="resources")

cardboard_blueprint = Blueprint('cardboard_blueprint', __name__,  template_folder=CARDBOARD_STATIC_DIR, static_folder=CARDBOARD_STATIC_DIR, static_url_path='/')


def get_assets():
    """
    Load and return the cardboard .js and .css assets from the cardboard index.html
    So that they may be included in parent flask app index html or passed to
    Flask templates.  The returned file paths are relative to the resources/ directory.
    """
    # Load the package and list files in the specified directory
    package = pkg_resources.files("cardboard") / "resources/assets"
    
    files_dict = {'js': None, 'css': None}
    
    for file in package.iterdir():
        # Convert the file to a string to get the filename
        filename = str(file.name)
        
        # Check if the file is a .js file
        if filename.endswith('.js'):
            files_dict['js'] = f"/assets/{filename}"

        # Check if the file is a .css file
        elif filename.endswith('.css'):
            files_dict['css'] = f"/assets/{filename}"

    return files_dict


@cardboard_blueprint.route('/cardboard')
def serve_react_app():
    """
    Serve index.html from vite dist
    """
    #return send_from_directory(cardboard_blueprint.static_folder, 'index.html')
    return render_template('index.html', cardboard_server=f"{request.scheme}://{CARDBOARD_FLASK_HOST}:{CARDBOARD_FLASK_PORT}")


@cardboard_blueprint.route('/<path:path>')
def serve_static(path):
    """
    Serve static files from vite dist
    """
    return send_from_directory(cardboard_blueprint.static_folder, path)


@cardboard_blueprint.route("/board")
def board():
    if cardboard.board_json is not None:
        return jsonify(cardboard.board_json)
    
    return jsonify({"error": f"{cardboard.board_json} not set."})


@cardboard_blueprint.route("/start")
def start():
    card_id = request.args.get("card")
    type = request.args.get("type")
    url = request.args.get("url")
    print(f"start {type} card {card_id} on {url}")
    retval = start_card(card_id, type, url)
    return jsonify(retval)


@cardboard_blueprint.route("/stop")
def stop():
    card_id = request.args.get("card")
    print(f"stop card {card_id}")
    retval = stop_card(card_id)
    return jsonify(retval)