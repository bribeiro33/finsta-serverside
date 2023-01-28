"""
Insta485 index (main) view.


URLs include:
/
"""
# import flask
# from flask import session, redirect, url_for
# import insta485
import arrow
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import uuid
import hashlib
import insta485

@insta485.app.route('/uploads/<path:filename>')
def file_url(filename):
    """Return picture."""
    #if 'username' in flask.session:
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename, as_attachment=True)
    flask.abort(404)

@insta485.app.route('/')
def show_index():
    """Display / route."""

    # Check if user's logged in, go to log in page if not
    if "user" not in session: 
        return redirect(url_for("is_logged"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()

    
    # Query posts
    #user = "awdeorio"
    cur = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE owner = ? "
        "UNION "
        "SELECT posts.postid, posts.filename, posts.owner, posts.created "
        "FROM following JOIN posts "
        "ON following.username2 = posts.owner "
        "WHERE following.username1 == ? "
        "ORDER BY postid DESC",
        (user, user, )
    )
    posts = cur.fetchall()
    for post in posts:
        
        # Correct post's img url
        post['img_url'] = flask.url_for("file_url", filename=post['filename'])

        # Correct timestamp format
        post['timestamp'] = arrow.get(post['created']).humanize()

        # GET post's owner's icon url
        cur_owner = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (post['owner'], )
        )
        post['owner_img_url'] = flask.url_for("file_url", filename=cur_owner.fetchone()['filename'])

        # GET comments
        cur_comments = connection.execute(
            "SELECT commentid, owner, postid, text "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY commentid ASC",
            (post['postid'], )
        )
        post['comments'] = cur_comments.fetchall()

        # GET likes
        cur_likes = connection.execute(
            "SELECT COUNT(owner) AS num_likes "
            "FROM likes "
            "WHERE postid = ?",
            (post['postid'], )
        )

        post['likes'] = cur_likes.fetchone()['num_likes']

        # GET if user likes the post
        cur_user_likes = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE owner=? AND postid=?",
            [user, post['postid']]
        )

        # Will return an entry if user likes the post
        if cur_user_likes.fetchone():
            post['user_likes_it'] = True
        else: 
            post['user_likes_it'] = False



    # Add database info to context
    context = {"posts": posts}
    return flask.render_template("index.html", **context)


    # ----------------------------------------------------------------

@insta485.app.route('/accounts/login/', methods=["GET"])
def is_logged():
    """GET if user logged in and login page"""

    # If user is logged in, redirect to home/index
    if "user" in session:
        return redirect(url_for("show_index"))

    # If user is not logged in, render login page
    return render_template("login.html")

def login():
    """POST user's login info"""
    # Recieve user info from form in login.html
    username = request.values.get('username')
    submitted_password = request.values.get('password')
    
    # If either field is empty, abort
    if not username or not submitted_password:
        abort(400)
    
    # Authenticate user information by checking db
    connection = insta485.model.get_db()
    cur_users = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )

    correct_pass = cur_users.fetchone()
    
    # If username doesn't have a password, abort
    if not correct_pass:
        abort(403)

    # Verify password by computing hashed pass w/ SHA512 of submitted password
    #   and comparing it against the db password
    algorithm, salt, db_password = correct_pass['password'].split('$')
    
    # Slightly modified from spec
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + submitted_password
    hash_obj.update(password_salted.encode('utf-8'))
    submitted_password_hash = hash_obj.hexdigest()
    
    if submitted_password_hash != db_password:
        abort(403)
    
    # Set session cookie w/ username
    session['user'] = username

# Can't be in post_accounts because not allowed to modify logout: name=operation
@insta485.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """POST logout of account request"""
    user = session.get('user')
    
    # Error somehwere if user is not logged in, safety
    if user:
        session.clear()
        
    return redirect(url_for('is_logged'))

@insta485.app.route('/accounts/create', methods=['GET'])
def create_account():
    #TODO: ALL OF IT
    return render_template("login.html") 

@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """All /accounts/ POST requests"""
    operation = request.values.get('operation')
    if operation == "login":
        login()
    
    else:
        return redirect(url_for('show_index'))
    
    # Redirect to what target arg equals in URL
    target = request.args.get('target')
    return redirect(target)