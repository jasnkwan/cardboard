##
# Project Makefile
#

.PHONY: start_flask \
		stop_flask \
		start_vite \
		stop_vite \
		start_server \
		stop_server \
		start_wsgi \
		stop_wsgi \
		build_vite


FLASK_DIR := ./cardboard
VITE_DIR  := ./cardboard_ui

FLASK_APP  := $(FLASK_DIR)/server.py
FLASK_HOST := localhost
FLASK_PORT := 5000

FLASK_CMD := FLASK_APP=$(FLASK_APP) flask run --debug --host $(FLASK_HOST) --port $(FLASK_PORT)
SERVE_CMD := python -m cardboard.server
WSGI_CMD  := gunicorn --bind $(FLASK_HOST):$(FLASK_PORT) cardbard.wsgi:app
VITE_CMD  := cd $(VITE_DIR) && npm run dev

STOP_FLASK_CMD := ps aux | grep ".venv/bin/flask" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
STOP_VITE_CMD  := ps aux | grep "cardboard_ui/node_modules/.bin/vite" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
STOP_SERVE_CMD := ps aux | grep "cardboard.server" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
BUILD_VITE_CMD := cd $(VITE_DIR) && npm run build


start_flask:
	@$(FLASK_CMD)

stop_flask:
	@$(STOP_FLASK_CMD)

start_vite:
	@$(VITE_CMD)

stop_vite:
	@$(STOP_VITE_CMD)

start_server:
	@$(SERVE_CMD)

stop_server:
	@$(STOP_SERVE_CMD)

start_wsgi:
	@$(WSGI_CMD)

stop_wsgi:
	@$(STOP_WSGI_CMD)

build_vite:
	@$(BUILD_VITE_CMD)

