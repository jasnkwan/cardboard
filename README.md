# Cardboard

![Project planning](https://img.shields.io/badge/status-planning-yellow.svg)

---
A simple data dashboard for use in Flask apps.  Each card on the board manages its own WebSocket connection to the server to be abe to handle multiple high bandwidth data sources such as audio or high frequency sensor data which could otherwise saturate a single multiplexed Flask SocketIO connection.

While this project was intended for use on localhost, it should be able to be deployed to the web as well, though we haven't needed to try this yet. This library is being created for a very specific use case in a private project, but perhaps someone out there will find it useful too.


## Prerequisites
- Python 3.7+
- Npm 10.8+
- GNU Make 3.8+


## Development

### Project Initialization
After cloning the repository, install backend and frontend dependencies. The make init target will install both backend and frontend dependencies.

#### Install Dependencies
```
make init
```

Alternatively, you can separately install the backend dependencies with pip and the frontend dependencies with npm.

#### Install Backend Dependencies with Pip
From the project root run pip install:
```
pip install -r requirements.txt
```

#### Install Frontend Dependencies with npm
From the cardboard_ui directory, run npm install:
```
cd cardboard_ui
npm install
```


### Start the Development Servers
For development, the Flask development server can be used to automatically reload when backend Python file changes are detected.  The Vite development server can be used to automatically reload when front-end Javascript or CSS files change.  The Flask server runs on http://127.0.0.1:5000.  The Vite server runs on http://127.0.0.1:5173.  When running the development servers, access the app from a webbrowser using the Vite server at http://127.0.0.1:5173.

1. Start the Flask development server:

```
make start_flask
```

2. Start the Vite development server:

```
make start_vite
```

### Start the WSGI Production Server
For production, Gunicorn is used to run the WSGI app on http://127.0.0.1:5000.  The Vite server is not used.  The front-end resources must be compiled and packaged and will be served by the production server.

1. Start the Gunicorn WSGI server:

```
make start_wsgi
```


## Installation of Published Packages

This section describes how to install the cardboard packages for development and production.  This assumes cardboard is being integrated into a Python Flask application with a front-end built using Vite with the React plugin.
In this context, we assume the basic directory structures:
```
project-root/
  .venv/
  flask-dir/  
    app.py
  ui-dir/  
    node_modules/  
    src/  
      main.jsx
      index.css
    vite.config.js
    package.json  
```


### Install Production Packages
### Backend
```
cd <project-root>
pip install cardboard
```
```
cd <ui-dir>
npm install cardboard-ui
```

### Installing from Local Dev Projects
This assums you've cloned the Cardboard git repository to `cardboard-project-root`.
#### Backend
```
pip install <cardboard-project-root>/dist/cardboard-<version>-py3-none-any.whl
```
#### Frontend
```
cd <cardboard-project-root>/cardboard_ui
npm link
```
```
cd <project-root>/<ui-dir>
npm link cardboard-ui
```

### Installing from TestPyPi
Use this command to install from the TestPyPi registry instead of the proeuction PyPi registry.
```
pip install -i https://test.pypi.org/simple/ cardboard
```

## Usage

1. Create an configure the Flask app for either developmet or production mode.
2. Load the Vite manifest
3. Import the cardboard blueprint into the Flask app.
4. Register the blueprint.
5. Load a json board configuration file.
6. Add the cardboard javascript and css assets to the Flask index.html template
7. Add a \<div> with the id 'root' to the \<body> of index.html.
8. Render the Board component into the root div in main.jsx.

### app.py
```python
"""
Example Flask cardboard server
"""
from flask import Flask, render_template, send_from_directory, jsonify, request
from cardboard import cardboard, blueprints
import os
import json

# Load environment variables
FLASK_ENV = os.environ.get("FLASK_ENV", default="production")
VITE_MANIFEST = os.environ.get("VITE_MANIFEST", default="./test_ui/dist/.vite/manifest.json")

# If development, serve static resources from the ui src, otherwise serve from ui dist
if FLASK_ENV == "development":
    app = Flask(__name__, template_folder="templates", static_folder="../test_ui/src")
else:
    app = Flask(__name__, template_folder="templates", static_folder="../test_ui/dist")

# Load the Vite manifest
manifest_file = "./test_ui/dist/.vite/manifest.json"
with open(manifest_file, "r") as f:
    manifest = json.load(f)

# Register cardboard blueprint routes
app.register_blueprint(blueprints.cardboard_blueprint)


@app.route("/")
def index():
    """
    Serve the index.html template, pass it the development mode and the server url
    :return: rendered index.html template
    """
    development = FLASK_ENV == "development"
    flask_server="http://127.0.0.1:5000"
    return render_template("index.html", development=development, flask_server=flask_server)


@app.route('/src/<path:file>')
def serve_src(file):
    """
    Serve the Vite .jsx or .css assets defined in the Vite manifest.
    This will be used only in production mode.  In development, the assets get served by the Vite dev server.
    :param file:
    :return:
    """
    global manifest
    path = request.path
    if path.startswith("/"):
        path = path[1:]

    if path.endswith(".css"):
        key = path.replace(".css", ".jsx")
        if key not in manifest:
            return jsonify({"Error": f"Manifest entry not found: {key}"}), 404
        if 'css' not in manifest[key]:
            return jsonify({"Error": f"No css for manifest entry {key}"}), 404
        css = manifest[key]['css']
        if len(css) == 0:
            return jsonify({"Error": f"CSS list for manifest entry {key} is empty"}), 404
        f = css[0]
    else:
        if path not in manifest:
            return jsonify({"Error": f"File not found: {path}"}), 404
        f = manifest[f'{path}']['file']
    return send_from_directory(app.static_folder, f)


if __name__ == "__main__":
    print(f"Hello cardboard")

    with open("./cards.json") as f:
        board_json = json.load(f)
        cardboard.configure_board(data=board_json)

    app.run(host="127.0.0.1", port=5000, debug=True)

```

### index.html
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hello, Cardboard</title>
  </head>

  <body style="width: 100vw; height: 100vh;">

    <!-- React container, Cardboard components well be rendered here -->
    <div id="root" style="width: 100%; height: 100%;"></div>

    <!-- Load the template data passed from the Flask server -->
    <script>
      const flask_server = "{{flask_server}}"
      const development = "{{development}}"
      console.log("flask_server=" + flask_server)
      console.log("development=" + development)
    </script>

    <!-- Refer to Vite Backend Integration documentation:            -->
    <!-- https://vite.dev/guide/backend-integration.html             -->

    {% if development %}

    <!-- If development mode, setup proxying to the Vite dev server. -->
    <!-- Make sure the Vite dev server is running on port 5173       -->
    <script type="module">
      console.log("DEV MODE!")
      import RefreshRuntime from 'http://localhost:5173/@react-refresh'
      RefreshRuntime.injectIntoGlobalHook(window)
      window.$RefreshReg$ = () => {}
      window.$RefreshSig$ = () => (type) => type
      window.__vite_plugin_react_preamble_installed__ = true
    </script>
    <script type="module" src="http://localhost:5173/@vite/client"></script>
    <script type="module" src="http://localhost:5173/src/main.jsx"></script>

    {% else %}

    <!-- If production mode, we serve the compiled assets from the flask server -->
    <!-- Vite dev server does not need to be running                            -->
    <script type="module" crossorigin src="/src/main.jsx"></script>
    <link rel="stylesheet" crossorigin href="/src/main.css">

    {% endif %}
  </body>
</html>
```

### main.jsx
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Board } from 'cardboard-ui'
import 'cardboard-ui/dist/style.css'

// Get the root div by Id and render the cardboard React component into it.
// Pass the flask_server template parameter (from the Flask server) to the Board component.
createRoot(document.getElementById('root')).render(
  <StrictMode>
  <div className="flex flex-col">
      <Board flask_server={flask_server} />
  </div>
  </StrictMode>,
)
```