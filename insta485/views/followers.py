"""
Insta485 followers view.


URLs include:
/users/<user_url_slug>/followers/
"""
# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


#same as following.py
@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def show_followers(user_url_slug):
    """Display followers route."""

    # Check if user's logged in, go to log in page if not
    if "user" not in session: 
        return redirect(url_for("login_page"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()
    
    # Abort if user_slug is not in db
    cur_user = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    dawg = cur_user.fetchone()
    if not dawg:
        abort(404)

    # get the followers of user_url_slug
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2=?",
        (user_url_slug, )
    )
    #username1 follows username2
    #the above gets all the rows of column 'username1' where username1 
    # follows the user

    #loop through all followers 
    # [{username1: golpari, username2: bdreyer}, 
    # {username1:bdreyer. username2: golpari}]
    f = cur.fetchall()
    for fol in f:
        # Formatting to fit into template name
        fol['username'] = fol['username1']
        
        # Check if user follows the people in the followers list
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1=? AND username2=?",
            (user, fol['username'], )
        )

        name = cur.fetchone()
        if name:
            fol['logname_follows_username'] = True
        else:
            fol['logname_follows_username'] = False

        # Get icon 
        cur_icon = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            (fol['username'], )
        )
        fol['user_img_url'] = flask.url_for("file_url", 
            filename=cur_icon.fetchone()['filename'])


    context = {'followers': f, 
        "logname": user_url_slug}
    return render_template("followers.html", **context)

