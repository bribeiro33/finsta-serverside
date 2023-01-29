"""
Insta485 following view.


URLs include:
/users/<user_url_slug>/following/
"""
# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


#same as following.py
@insta485.app.route('/users/<user_url_slug>/following/', methods=["GET"])
def show_following(user_url_slug):
    """Display following route."""

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

    # get the followings of username1 where username2 is a followedPerson by username1
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=?",
        (user_url_slug, )
    )
    #username1 follows username2
    #the above gets all the rows of column 'username1' where username1 follows the user

    #loop through all followers [{username1: golpari, username2: bdreyer}, {username1:bdreyer. username2: golpari}]
    f = cur.fetchall()
    for fol in f:
        # Formatting to fit into template name
        fol['username'] = fol['username2']
        
        # Check if user is following the people in the following list
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1=? AND username2=?",
            (user, fol['username'], )
        )

        name = cur.fetchone()['username2']
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
        fol['user_img_url'] = flask.url_for("file_url", filename=cur_icon.fetchone()['filename'])


    context = {'following': f, 
        "username": user_url_slug}
    return render_template("following.html", **context)

#not from followers! the POST request!
@insta485.app.route('/users/<user_url_slug>/following/', methods=["POST"])
def change_following(user_url_slug):
    """Change following route: ALL /following/?target=URL POST requests"""

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
    
    operation = request.values.get('operation')
        
    #find when user follows otheruser, and get the entire row from the table
    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1=? and username2=?",
        (user, user_url_slug)
    )
    folling = cur.fetchall()

    
    if operation == 'follow':
        #tries to follow a user that they already follow
        if folling:
            abort(409)

        #otherwise just follow the account!
        else:
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES "
                "(?, ?)", (user, user_url_slug,)
            )
    
    
    if operation == 'unfollow':
        #tries to unfollow a user that they do not follow
        if not folling:
            abort(409)
        #otherwise just unfollow the account!
        else:
            #delete username1 from following username2
            connection.execute(
                "DELETE FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (user, user_url_slug,)
            )

    targeturl = request.args.get("target")
    #redirect to target if it is set
    if targeturl:
        return redirect(targeturl)
    #redirect to index if no target specified
    else:
        return redirect(url_for('show_index'))


"""
Insta485 following view.


URLs include:
/

# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485

@insta485.app.route('/uploads/<path:filename>')
def file_url(filename):
    Return picture.
    #if 'username' in flask.session:
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename, as_attachment=True)
    flask.abort(404)

#same as followers.py
@insta485.app.route('/users/<user_url_slug>/following/', methods=["GET"])
def show_following(user_url_slug):
    "Display following route."

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
    return render_template("following.html", **context) """