"""
Insta485 explore view.


URLs include:
/explore/
"""
# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


#same as following.py
@insta485.app.route('/explore/', methods=["GET"])
def explore(user_url_slug):
    # Add database info to context
    context = {"explore": explore}
    return flask.render_template("explore.html", **context)