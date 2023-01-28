"""
Insta485 following view.


URLs include:
/
"""
# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485

@insta485.app.route('/uploads/<path:filename>')
def file_url(filename):
    """Return picture."""
    #if 'username' in flask.session:
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename, as_attachment=True)
    flask.abort(404)

#same as followers.py
@insta485.app.route('/users/<user_url_slug>/following/', methods=["GET"])
def show_following(user_url_slug):
    """Display following route."""

    # Check if user's logged in, go to log in page if not
    if "user" not in session: 
        return redirect(url_for("is_logged"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()

    # get the followers of user_url_slug
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2=?",
        [user_url_slug]
    )


    #loop through all followers
    f = cur.fetchall()
    for fol in f:
        fol['username'] = fol['username1']
        
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1=? AND username2=?",
            [user, fol['username']]
        )
        
        #not super sure how i feel abt this logic, I was trying to go based on accounts.py
        name = cur.fetchone()
        #if user is empty, then abort
        if not name:
            abort(404)
        if name:
            fol['logname_follows_username'] = True
        else:
            fol['logname_follows_username'] = False

    context = {'following': f, 
        "username": user_url_slug}
    return render_template("following.html", **context)