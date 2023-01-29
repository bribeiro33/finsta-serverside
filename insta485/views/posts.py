"""
Insta485 posts view.



URLs include:
/posts/
/posts/<postid_url_slug>/
"""
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import uuid
import pathlib
import os
import insta485
import arrow

@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def post_page(postid_url_slug):
    """GET singular post page, redirect to login if not logged in"""
    if "user" not in session: 
        return redirect(url_for("login_page"))

    user = session["user"]
    connection = insta485.model.get_db()

    cur_post = connection.execute(
        "SELECT filename, owner, created "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug, )
    )

    post = cur_post.fetchone()

    # Slug = postid
    post['postid'] = postid_url_slug
    # Correct post's img url
    post['img_url'] = url_for("file_url", filename=post['filename'])

    # Correct timestamp format
    post['timestamp'] = arrow.get(post['created']).humanize()

    # Query post's owner's icon url
    cur_owner = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (post['owner'], )
    )
    post['owner_img_url'] = flask.url_for("file_url", filename=cur_owner.fetchone()['filename'])

    # Query comments
    cur_comments = connection.execute(
        "SELECT commentid, owner, postid, text "
        "FROM comments "
        "WHERE postid = ? "
        "ORDER BY commentid ASC",
        (post['postid'], )
    )
    post['comments'] = cur_comments.fetchall()

    # Query likes
    cur_likes = connection.execute(
        "SELECT COUNT(owner) AS num_likes "
        "FROM likes "
        "WHERE postid = ?",
        (post['postid'], )
    )

    post['likes'] = cur_likes.fetchone()['num_likes']

    # Query if user likes the post
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

    post['logname'] = user
    return render_template("post.html", **post)

def post_create():
    """POST a new post"""
    # Abort (backup) if user not logged in
    if "user" not in session:
        abort(403)
    
    connection = insta485.model.get_db()
    file_obj = flask.request.files["file"]
    # Abort if no file was submitted
    if not file_obj: 
        abort(400)
    
    # Format new post pic
    # Unpack flask obj
    filename = file_obj.filename

    # Compute base name
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    file_obj.save(path)

    # Insert into database
    connection.execute(
        "INSERT INTO "
        "posts(filename, owner) "
        "VALUES (?,?)",
        (uuid_basename, session['user'], )
    )

def post_delete():
    """POST a post deletion"""
    # Abort (backup) if user not logged in
    if "user" not in session:
        abort(403)
    
    # Get postid of desired post from form
    postid = flask.request.form['postid']

    # Get post owner and filename from db
    connection = insta485.model.get_db()
    cur_file = connection.execute(
        "SELECT owner, filename "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    post = cur_file.fetchone()

    # Verify that user logged in is the post's owner
    if session['user'] != post['owner']:
        abort(403)

    # Delete post_img's file
    filename = post['filename']
    filepath = insta485.app.config["UPLOAD_FOLDER"]/filename
    os.remove(filepath)
    
    # Remove post from database
    connection.execute(
        "DELETE "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )

@insta485.app.route('/posts/', methods=['POST'])
def post_action():
    """POST possible post actions - create, delete"""
    operation = request.values.get('operation')
    if operation == 'create':
        post_create()
    elif operation == 'delete':
        post_delete()
    
    # Redirect to what target arg equals in from's action URL 
    target_url = request.args.get('target')

    # If target not set, redirect to /users/<logname>/
    if not target_url:
        target_url = url_for('user_page', user_url_slug=session['user'])
    return redirect(target_url)
