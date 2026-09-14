#!/usr/bin/env bash
set -e
python src/etl/loader.py
pytest -q