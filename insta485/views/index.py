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
import insta485

# @insta485.app.route('/uploads/<path:filename>')
# def file_url(filename):
#     """Return picture."""
#     #if 'username' in flask.session:
#     #TODO check file permissions, cookies
#     return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
#                                          filename, as_attachment=True)
#     flask.abort(404)

@insta485.app.route('/')
def show_index():
    """Display / route."""

    # Check if user's logged in, go to log in page if not
    if "user" not in session: 
        return redirect(url_for("login_page"))

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



    # Add database info to context
    context = {"posts": posts}
    return flask.render_template("index.html", **context)


