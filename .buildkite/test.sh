#!/bin/sh

pip install -r requirements-test.txt
pip install -e .
py.test tests/ -p no:sugar --verbose --junitxml=pytest-${BUILDKITE_JOB_ID}.xml
