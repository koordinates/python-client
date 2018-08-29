#!/bin/sh

pip install -r requirements-test.txt
pip install dist/*.whl
py.test tests/ -p no:sugar --verbose --junitxml=pytest-${BUILDKITE_JOB_ID}.xml
