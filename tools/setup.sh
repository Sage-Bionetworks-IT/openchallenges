#!/usr/bin/env bash

# Safer bash scripts
set -euxo pipefail

# Install Node.js dependencies
npm install -g aws-cdk@2.151.0

# Install Python dependencies
pip install --upgrade pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Install git hooks
git config --global --add safe.directory "$PWD"
pre-commit install --install-hooks
