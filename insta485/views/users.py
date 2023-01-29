
"""
Insta485 users view.
   

URLs include:
/users/<user_url_slug>/
"""
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import uuid
import pathlib
import os
import insta485
from insta485 import model
import arrow

@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def user_page(user_url_slug):
    return render_template("user.html")