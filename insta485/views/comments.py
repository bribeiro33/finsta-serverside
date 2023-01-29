"""
Insta485 comment actions view.



URLs include:
/comments/
"""
import flask
from flask import (session, redirect, url_for, request, abort)
import insta485

@insta485.app.route('/comments/', methods=['POST'])
def comment_action():
    """POST all /comments/?target= requests - create and delete"""
    # Get info from form
    operation = request.values.get('operation')
    postid = request.form['postid']
    commentid = request.form['commentid']

    if operation == 'create':
        text = request.form['text']
        # Abort if user tries to create an empty comment
        if text == '': 
            abort(400)
        
        #POST new comment
        connection.execute(
            "INSERT INTO "
            "comments(owner, postid, text) "
            "VALUES (?, ?, ?)",
            (session['user'], postid, text)
        )

    elif operation == 'delete':
        # Use db to make sure user is comment owner
        connection = insta485.model.get_db()
        cur_owner = connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE owner = ? AND commentid = ?",
            (session['user'], commentid, )
        )
        is_owner = cur_owner.fetchone()
        # Abort if user is not comment owner
        if not is_owner: 
            abort(403)
        # Delete comment using commentid
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
    # Redirect to what target arg equals in from's action URL 
    target_url = request.args.get('target')
    # For whatever reason, when ?target=/, target evaluates to None
    if not target_url:
        target_url = "/"
    return redirect(target_url)