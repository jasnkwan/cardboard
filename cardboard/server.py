"""
Flask server
"""

import json

from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from cardboard.cardboard import start_card, stop_card
from cardboard import cardboard

import os
import atexit


load_dotenv()

PROJECT_NAME = os.environ.get("PROJECT_NAME", default="cardboard")

FLASK_HOST = os.environ.get("FLASK_HOST", default="localhost")
FLASK_PORT = int(os.environ.get("FLASK_PORT", default="5000"))
FLASK_ENV = os.environ.get("FLASK_ENV", default="production")

VITE_HOST = os.environ.get("VITE_HOST", default="localhost")
VITE_PORT = int(os.environ.get("VITE_PORT", default="5173"))

CARDBOARD_CONFIG = os.environ.get("CARDBOARD_CONFIG", default="")

print(f"Environment:")
print(f"  PROJECT_NAME={PROJECT_NAME}")
print(f"  FLASK_ENV={FLASK_ENV}")
print(f"  FLASK_HOST={FLASK_HOST}")
print(f"  FLASK_PORT={FLASK_PORT}")
print(f"  VITE_HOST={VITE_HOST}")
print(f"  VITE_PORT={VITE_PORT}")
print(f"  CARDBOARD_CONFIG={CARDBOARD_CONFIG}")

manifest = None

# Load the board configuration
if os.path.exists(f"{CARDBOARD_CONFIG}"):
    with open(f"{CARDBOARD_CONFIG}") as f:
        import json
        board_json = json.load(f)
        cardboard.configure_board(data=board_json)
else:
    print(f"Board config file {CARDBOARD_CONFIG} does not exist.")

# Flask setup, serve static files from vite dist folder

if FLASK_ENV == "development":
    static_folder = f"../{PROJECT_NAME}_ui"
    template_folder = f"../{PROJECT_NAME}_ui"
else:
    import importlib.resources as pkg_resources
    from . import resources
    from . import templates
    static_folder = pkg_resources.files(resources)
    template_folder = pkg_resources.files(templates)
    static_folder = str(static_folder._paths[0])
    template_folder = str(template_folder._paths[0])
    with open(os.path.join(static_folder, ".vite", "manifest.json"), "r") as f:
        manifest = json.load(f)

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = os.environ.get("APP_SECRET_KEY", default="app_secret_key")
app.url_map.strict_slashes = False

cors = CORS(app, origins=[f"http://localhost:{VITE_PORT}", f"https://localhost:{VITE_PORT}",
                          f"http://127.0.0.1:{VITE_PORT}", f"https://127.0.0.1:{VITE_PORT}",
                          f"http://localhost:{FLASK_PORT}", f"https://localhost:{FLASK_PORT}",
                          f"http://127.0.0.1:{FLASK_PORT}", f"https://127.0.0.1:{FLASK_PORT}"])

# Register an at-exit listener to do any necessary cleanup
# Add any cleanup steps here.
def cleanup():
    print(f"Cleanup on exit")
    
atexit.register(cleanup)


def get_modules(key="src/main.jsx"):
    """
    Parse the list of modules and imports from vite manifest
    Args:
        key (str, optional): manifest key. Defaults to "src/main.jsx".

    Returns:
        list: modules
        list: imports
    """
    modules = []
    imported = []
    
    cjs = manifest[key]["file"]
    es = cjs.replace("cjs", "es")
    
    # use the es module for serving the app in the browser
    modules.append(es)
    
    # get the list of imports for pre-loading
    if "imports" in manifest[key]:
        for import_key in manifest[key]["imports"]:
            imported.append(manifest[import_key]["file"])
        
    return modules,imported


def get_styles():
    """
    Parse the list of css resources from vite manifest
    :return: list of css resources in manifest
    """
    styles = []
    for key,val in manifest.items():
        if key.endswith(".css"):
            styles.append(val["file"])
        if "css" in val:
            for css in val["css"]:
                styles.append(css)
            
    return styles


def serve_development(request):
    """
    Serve index.html from vite dist, assumes vites server is running on VITE_HOST:VITE_PORT
    :return: index.html
    """
    flask_host = "127.0.0.1" if FLASK_HOST == "0.0.0.0" else FLASK_HOST
    vite_host = "127.0.0.1" if VITE_HOST == "0.0.0.0" else VITE_HOST
    title = PROJECT_NAME
    print(f"serve_development: flask_host={flask_host}, vite_host={vite_host}")
    return render_template("index.html", title=f"{title}", flask_server=f"{request.scheme}://{flask_host}:{FLASK_PORT}", vite_server=f"{request.scheme}://{vite_host}:{VITE_PORT}", development=True, tags=[])


def serve_production(request):
    """
    Serve index.html from flask dist
    :return: index.html
    """
    modules = []
    imported = []
    styles = []
    
    modules,imported = get_modules(key="src/main.jsx")
    styles = get_styles()
    
    tags = []
    for module in modules:
        tags.append(f"<script type='module' crossorigin src='/{module}'></script>")
    for imp in imported:
        tags.append(f"<link rel='modulepreload' crossorigin href='/{imp}' />")
    for style in styles:
        tags.append(f"<link rel='stylesheet' crossorigin href='/{style}' />")
        
    server_host = "127.0.0.1" if FLASK_HOST == "0.0.0.0" else FLASK_HOST
    title = PROJECT_NAME    
    return render_template("index.html", title=f"{title}", flask_server=f"{request.scheme}://{server_host}:{FLASK_PORT}", development=False, tags=tags)


@app.route("/<path:file>")
def serve_static(file):
    """
    Serve static files from vite dist
    :param path: path of file to serve
    :return: the file
    """
    
    path = request.path
    if path.startswith("/"):
        path = path[1:]
        
    return send_from_directory(app.static_folder, file)


@app.route("/")
def serve_react_app():
    """
    Serve index.html from vite dist
    :return: index.html
    """
    if FLASK_ENV == "development":
        return serve_development(request)
    else:
        return serve_production(request)


@app.route("/board")
def board():
    if cardboard.board_json is not None:
        return jsonify(cardboard.board_json)
    
    return jsonify({"error": f"{cardboard.board_json} not set."})


@app.route("/start")
def start():
    card_id = request.args.get("card")
    type = request.args.get("type")
    url = request.args.get("url")
    provider = request.args.get("provider")
    print(f"start {type} card {card_id} on {url} with provider {provider}")
    retval = start_card(card_id=card_id, card_type=type, card_url=url, card_provider=provider)
    return jsonify(retval)


@app.route("/stop")
def stop():
    card_id = request.args.get("card")
    print(f"stop card {card_id}")
    retval = stop_card(card_id)
    return jsonify(retval)



if __name__ == "__main__":
    print(f"Starting Flask Server...")
    app.run(debug=True, host="0.0.0.0", port=5555)


'''

from flask import Flask
from flask_cors import CORS

from cardboard.blueprints import cardboard_blueprint
from cardboard import cardboard

import os


app = Flask(__name__)
cors = CORS(app, origins=['*', 'http://localhost:5173', "http://127.0.0.1:5173"])


app.register_blueprint(cardboard_blueprint)

# Load the board configuration
if os.path.exists("./tests/data/cards.json"):
    with open("./tests/data/cards.json") as f:
        import json
        board_json = json.load(f)
        cardboard.configure_board(data=board_json)


if __name__ == '__main__': 
    app.run(host="127.0.0.1", port=5000, debug=True)
'''
