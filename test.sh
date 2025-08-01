#!/usr/bin/env bash

# This script runs the tests for the FastAPI application using pytest.
db_url='sqlite:///output/test.db' pytest test.py -svv