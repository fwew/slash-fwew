#!/usr/bin/env bash

# create python3 virtual environment
python3 -m venv venv && \

# activate environment
source venv/bin/activate && \

# install dependencies
pip install -r requirements.txt
