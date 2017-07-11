@echo off
pip install -r requirements.txt
set FLASK_APP=flaskr
set FLASK_DEBUG=true
flask run