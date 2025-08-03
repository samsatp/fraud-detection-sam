#!/usr/bin/env bash

output_db='output/test.db'

# This script runs the tests for the FastAPI application using pytest.
db_url=sqlite:///$output_db pytest test.py -svv

# Clean up the test database after running tests
rm $output_db