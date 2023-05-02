# Development default values
#
# To customize locally, create a `config.custom.Makefile` file

API_PORT ?= 5000
HOST ?= 0.0.0.0

export PROJECT_NAME = pellov
export FLASK_APP = $(PWD)/$(PROJECT_NAME).py
export WWWPELLOV_CONFIG := $(PWD)/www-pellov.cfg

# Python env
PYTHON_ONLY = 1
VENV = $(PWD)/.env
PYTHON ?= python3.8
PYTHON_SRCDIR = $(PWD)

URL_PROD = https://www.promomaker.fr
