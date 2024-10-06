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
		build_vite \
		clean \
		clobber


FLASK_DIR        := ./cardboard
VITE_DIR         := ./cardboard_ui
VITE_DIST_DIR    := $(VITE_DIR)/dist
DIST_DIR         := ./dist
BUILD_DIR        := ./build
EGG_INFO_DIR     := ./cardboard.egg-info
NODE_MODULES_DIR := $(VITE_DIR)/node_modules
PYCACHE_DIR      := $(FLASK_DIR)/__pycache__

FLASK_APP  := $(FLASK_DIR)/server.py
FLASK_HOST := 127.0.0.1
FLASK_PORT := 5000

INIT_CMD        := pip install -r requirements.txt
NPM_INSTALL_CMD := cd $(VITE_DIR) && npm install
FLASK_CMD       := FLASK_APP=$(FLASK_APP) flask run --debug --host $(FLASK_HOST) --port $(FLASK_PORT)
SERVE_CMD       := python -m cardboard.server
WSGI_CMD        := gunicorn --bind $(FLASK_HOST):$(FLASK_PORT) cardbard.wsgi:app
VITE_CMD        := cd $(VITE_DIR) && npm run dev

STOP_FLASK_CMD := ps aux | grep ".venv/bin/flask" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
STOP_VITE_CMD  := ps aux | grep "cardboard_ui/node_modules/.bin/vite" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
STOP_SERVE_CMD := ps aux | grep "cardboard.server" | grep -v grep | awk '{print $$2}' | xargs -r kill -2
BUILD_VITE_CMD := cd $(VITE_DIR) && npm run build
BUILD_DIST_CMD := python setup.py sdist bdist_wheel

init:
	@echo "Installing Python packages..."
	@$(INIT_CMD)
	@echo "Installing Node packages..."
	@$(NPM_INSTALL_CMD)

start_flask:
	@$(FLASK_CMD)

stop_flask:
	@$(STOP_FLASK_CMD)

start_vite:
	@$(VITE_CMD)

stop_vite:
	@$(STOP_VITE_CMD)

start_server: $(VITE_DIST_DIR)
	@$(SERVE_CMD)

stop_server:
	@$(STOP_SERVE_CMD)

start_wsgi: $(VITE_DIST_DIR)
	@$(WSGI_CMD)

stop_wsgi:
	@$(STOP_WSGI_CMD)

build_vite:
	@$(BUILD_VITE_CMD)

dist: $(VITE_DIST_DIR)
	@$(BUILD_DIST_CMD)

clean:
	@rm -rf $(VITE_DIST_DIR)
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DIST_DIR)
	@rm -rf $(EGG_INFO_DIR)

clobber: clean
	@rm -rf $(NODE_MODULES_DIR)
	@rm -rf $(PYCACHE_DIR)

$(VITE_DIST_DIR):
	@$(BUILD_VITE_CMD)