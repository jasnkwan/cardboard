# Cardboard

![Project planning](https://img.shields.io/badge/status-planning-yellow.svg)

---
A simple data dashboard for Flask apps.


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


## Installation

### Installing from Local Dev Project
```
pip install <cardboard-project-root>/dist/cardboard-<version>-py3-none-any.whl
```

### Installing from TestPyPi
```
pip install -i https://test.pypi.org/simple/ cardboard
```

## Usage

1. Import the cardboard blueprint into the Flask app.
2. Register the blueprint.
3. Load a json board configuration file.
4. Add the cardboard javascript and css assets to the Flask index.html template
5. Add a \<div> with the id 'root' to the \<body> of index.html.

### app.py
```python
from flask import Flask, render_template
from cardboard import cardboard, blueprints

import json

app = Flask(__name__, template_folder="templates")

app.register_blueprint(blueprints.cardboard_blueprint)

@app.route("/")
def index():
    return render_template("index.html")

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
    <title>Cardboard</title>
    <script type="module" crossorigin src="/assets/index-SZaSMXbb.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-BmzdEL9M.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>

```