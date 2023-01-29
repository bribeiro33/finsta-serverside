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
def explore():
    """Display explore route."""

    # Check if user's logged in, go to log in page if not
    if "user" not in session: 
        return redirect(url_for("login_page"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()
    
    """ # Abort if user_slug is not in db
    cur_user = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    dawg = cur_user.fetchone()
    if not dawg:
        abort(404) """
    
    #get the usernames of NONFOLLOWED people, so you have to check that they arent in the user's follows list
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username!=?"
        "AND username NOT IN ( "
        "SELECT username2 "
        "FROM following "
        "WHERE username1=?)",
        (user, user, )
    )
    all_users = cur.fetchall()
    
    for u in all_users:
        # Get icon 
        cur_icon = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            (u['username'], )
        )
        u['user_img_url'] = flask.url_for("file_url", filename=cur_icon.fetchone()['filename'])
    
    # Add database info to context
    context = {"explore": explore}
    return flask.render_template("explore.html", **context)