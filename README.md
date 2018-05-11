# whiteboard-with-friends-py
Practicing full-stack dev with an app previously made by Rob Quinn and me
=======
[Flask Heroku Sample](https://whiteboard-with-friends-py.herokuapp.com)
====================

A simple Python Flask example application that's ready to run on Heroku.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Development Setup

* `virtualenv wwf`

* `echo "wwf" >> .gitignore`

* `source wwf/Scripts/activate`

* `pip install -r requirements.txt`

* `pip install Django`

* `django-admin startproject project`

## Run Locally

* `python app\manage.py runserver`

## Deploy

* `heroku create`

* `heroku addons:create heroku-postgresql:hobby-dev`

* `git push heroku master`

## Contributors

* [Spectrum](http://bgrins.github.io/spectrum)
