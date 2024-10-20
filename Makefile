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
		init \
		info \
		build_vite \
		dist \
		depends \
		version \
		tag \
		upload_test_pypi \
		upload_pypi \
		upload_npm \
		publish \
		clean \
		clean_vite \
		clean_dist \
		clobber


# Deduce the project root directory. Assuemes this Makefile is in project root.
MAKEFILE_PATH    := $(abspath $(lastword $(MAKEFILE_LIST)))
PROJECT_DIR      := $(patsubst %/,%,$(dir $(MAKEFILE_PATH)))

PROJECT_NAME     := cardboard
VERSION          := $(shell cat $(PROJECT_DIR)/VERSION)

# Bulid artifact names
PYTHON_BDIST_WHL := cardboard_server-$(VERSION)-py3-none-any.whl
PYTHON_SDIST_ZIP := cardboard_server-$(VERSION).tar.gz
NODE_MODULE_ZIP  := cardboard-ui-$(VERSION).tar.gz

# Directory setup
FLASK_DIR        := ./cardboard
VITE_DIR         := ./cardboard_ui
FLASK_RES_DIR    := $(FLASK_DIR)/resources
VITE_DIST_DIR    := $(VITE_DIR)/dist
VITE_SRC_DIR     := $(VITE_DIR)/src
DIST_DIR         := ./dist
BUILD_DIR        := ./build
EGG_INFO_DIR     := ./cardboard_server.egg-info
NODE_MODULES_DIR := $(VITE_DIR)/node_modules
PYCACHE_DIR      := $(FLASK_DIR)/__pycache__

FLASK_APP        := $(FLASK_DIR)/server.py
FLASK_HOST       := 127.0.0.1
FLASK_PORT       := 5000

INIT_CMD         := pip install -r requirements.txt
NPM_INSTALL_CMD  := cd $(VITE_DIR) && npm install

# Configure Command Macros
FLASK_CMD        := FLASK_APP=$(FLASK_APP) FLASK_ENV=development flask run --debug --host $(FLASK_HOST) --port $(FLASK_PORT)
SERVE_CMD        := python -m cardboard.server
WSGI_CMD         := gunicorn --bind $(FLASK_HOST):$(FLASK_PORT) cardboard.wsgi:app
VITE_CMD         := cd $(VITE_DIR) && npm run dev

STOP_FLASK_CMD   := ps aux | grep ".venv/bin/flask" | grep -v grep | awk '{print $$2}' | xargs -r kill -2 && lsof -i :$(FLASK_PORT) | awk '{print $$2}' | grep -v PID | xargs -r kill -9 > /dev/null 2>&1
STOP_SERVE_CMD   := ps aux | grep "cardboard.server" | grep -v grep | awk '{print $$2}' | xargs -r kill -2 && lsof -i :$(FLASK_PORT) | awk '{print $$2}' | grep -v PID | xargs -r kill -9 > /dev/null 2>&1
STOP_WSGI_CMD    := ps aux | grep "cardboard.wsgi:app" | grep -v grep | awk '{print $$2}' | xargs -r kill -2 && lsof -i :$(FLASK_PORT) | awk '{print $$2}' | grep -v PID | xargs -r kill -2 > /dev/null 2>&1
STOP_VITE_CMD    := ps aux | grep "cardboard_ui/node_modules/.bin/vite" | grep -v grep | awk '{print $$2}' | xargs -r kill -2

BUILD_VITE_CMD   := cd $(VITE_DIR) && npm run build
FREEZE_CMD       := pip freeze > requirements.txt
DEPENDS_CMD      := python build_utils/update_dependencies.py
SETUP_CMD        := python setup.py sdist bdist_wheel
COPY_ASSETS_CMD  := cp -r $(VITE_DIST_DIR) $(FLASK_RES_DIR)
COPY_REACT_CMD   := cp -r $(VITE_SRC_DIR)/* $(FLASK_RES_DIR)/.
BUILD_DIST_CMD   := python -m build
ZIP_VITE_CMD     := tar cfzv $(DIST_DIR)/$(NODE_MODULE_ZIP) -C $(VITE_DIST_DIR) .

UPLOAD_TEST_PYPI_CMD  := twine upload --verbose --repository testpypi dist/*
UPLOAD_PYPI_CMD  := twine upload --verbose dist/*     
UPLOAD_NPM_CMD   := cd $(VITE_DIR) && npm publish

UPDATE_VERSION_CMD := python build_utils/update_versions.py
TAG_CMD          := cd $(PROJECT_DIR) && git tag -a v$(VERSION) -m "Create version tag v$(VERSION)" && git push origin v$(VERSION)



#
# Print info
#
info:
	@echo "MAKEFILE_LIST:     $(MAKEFILE_LIST)"
	@echo "PROJECT_DIR:       $(PROJECT_DIR)"
	@echo "VERSION:           $(VERSION)"
	@echo "NODE_MODULE_ZIP:   $(NODE_MODULE_ZIP)"
	@echo "PYTHON_BDIST_WHL:  $(PYTHON_BDIST_WHL)"
	@echo "PYTHON_SDIST_ZIP:  $(PYTHON_SDIST_ZIP)"

#
# Install project dependencies
#
init:
	@echo "Installing Python packages..."
	@$(INIT_CMD)
	@echo "Installing Node packages..."
	@$(NPM_INSTALL_CMD)

#
# Start the Flask development server
#
start_flask:
	@$(FLASK_CMD)

#
# Stop the Flask development server
#
stop_flask:
	@$(STOP_FLASK_CMD)

#
# Start the Vite development server
#
start_vite:
	@$(VITE_CMD)

#
# Stop the Vite development server
#
stop_vite:
	@$(STOP_VITE_CMD)

#
# Start the Flask server in debug mode with Python
#
start_server: $(VITE_DIST_DIR)
	@$(SERVE_CMD)

#
# Stop the Flask server
#
stop_server:
	@$(STOP_SERVE_CMD)

#
# Start the Gunicorn WSGI server
#
start_wsgi:
	@$(WSGI_CMD)

#
# Stop the Gunicorn WSGI server
#
stop_wsgi:
	@$(STOP_WSGI_CMD)

#
# Build the Vite production assets
#
build_vite:
	@$(BUILD_VITE_CMD)

#
# Build Python packages
#
build_python: $(DIST_DIR)/$(PYTHON_BDIST_WHL) $(DIST_DIR)/$(PYTHON_BDIST_WHL)
	

#
# Update Python dependencies in requirements.txt and pyproject.toml
#
depends:
	@$(FREEZE_CMD)
	@$(DEPENDS_CMD)

#
# Build source and binary wheel distributions
#
dist: $(VITE_DIST_DIR) $(DIST_DIR)/$(PYTHON_BDIST_WHL) $(DIST_DIR)/$(PYTHON_BDIST_WHL) $(DIST_DIR)/$(NODE_MODULE_ZIP)
#	@$(COPY_ASSETS_CMD)
#	@$(COPY_REACT_CMD)
#	@rm -rf $(FLASK_RES_DIR)

#
# Update versions in pyproject.toml and package.json to match VERSION
#
versions:
	@$(UPDATE_VERSION_CMD)

#
# Create a tagged release with the version number in VERSION. This will trigger the create_release.yml workflow.
#
tag:
	@$(TAG_CMD)

#
# Upload packages to TestPyPi server.
# 
upload_test_pypi: $(DIST_DIR)/$(PYTHON_BDIST_WHL) $(DIST_DIR)/$(PYTHON_BDIST_WHL) 
	@$(UPLOAD_TEST_PYPI_CMD)

#
# Upload packages to PyPi server.
# 
upload_pypi: $(DIST_DIR)/$(PYTHON_BDIST_WHL) $(DIST_DIR)/$(PYTHON_BDIST_WHL) 
	@$(UPLOAD_PYPI_CMD)

#
# Upload ui packages to npm.
#
upload_npm: $(VITE_DIST_DIR)
	@$(UPLOAD_NPM_CMD)

#
# Publish to PYPI and NPM
#
publish: dist
	@$(UPLOAD_PYPI_CMD)
	@$(UPLOAD_NPM_CMD)

#
# Remove Vite build files
#
clean_vite:
	@rm -rf $(VITE_DIST_DIR)

#
# Remove Python package build files
#
clean_dist:
	@rm -rf $(FLASK_RES_DIR)
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DIST_DIR)
	@rm -rf $(EGG_INFO_DIR)

#
# Remove Python and Vite build files
#
clean: clean_vite clean_dist

#
# Remove Python and Vite build files, installed node modules, and python dependencies
#
clobber: clean
	@rm -rf $(NODE_MODULES_DIR)
	@rm -rf $(PYCACHE_DIR)

#
# Create the Vite build directory
#
$(VITE_DIST_DIR):
	@$(BUILD_VITE_CMD)

#
# Copy vite build dir to the Flask res directory
#
$(FLASK_RES_DIR): $(VITE_DIST_DIR)
	@$(COPY_ASSETS_CMD)

#
# Build python package artifacts
#
$(DIST_DIR)/$(PYTHON_BDIST_WHL):
	@$(BUILD_DIST_CMD)

#
# Build python package artifacts
#
$(DIST_DIR)/$(PYTHON_SDIST_ZIP):
	@$(BUILD_DIST_CMD)

#
# Build node module artifacts
#
$(DIST_DIR)/$(NODE_MODULE_ZIP): $(VITE_DIST_DIR)	
	@echo "Building node module archive..."
	@$(ZIP_VITE_CMD)
	@echo "Built node module archive."