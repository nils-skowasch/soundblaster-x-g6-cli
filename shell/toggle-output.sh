#!/bin/bash
python_bin="$(dirname $0)/../venv/bin/python"
python_file="$(dirname $0)/../g6_cli.py"
eval "$python_bin $python_file --toggle-output"
