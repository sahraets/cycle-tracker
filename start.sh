#!/bin/bash
source venv/bin/activate
python app/api.py &
open http://127.0.0.1:5500/frontend/index.html

