"""
Insta485 followers view.


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

@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def show_followers(user_url_slug):
    """Display / route."""

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

     #dawg i have no idea what is going on and i am not exaggerating when 
    # I say ive been working for multiple hours and feeling like a friggin 
    # fool i havent been able to write a single full file

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
        
        if cur.fetchone():
            fol['logname_follows_username'] = True
        else:
            fol['logname_follows_username'] = False

    context = {'followers': f, 
        "username": user_url_slug}
    return render_template("followers.html", **context)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)