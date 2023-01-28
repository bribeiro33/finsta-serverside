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
from insta485 import model
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
