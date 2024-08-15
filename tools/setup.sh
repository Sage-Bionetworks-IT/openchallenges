#!/usr/bin/env bash

# Safer bash scripts
set -euxo pipefail

npm install -g aws-cdk@2.151.0

pip install --upgrade pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

git config --global --add safe.directory "$PWD"
pre-commit install-hooks
