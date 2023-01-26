"""
Insta485 index (main) view.


URLs include:
/
"""
import flask
import insta485
import arrow

# # @insta485.app.route('/uploads/<path:filename>')
# # def file_url(filename):
# #     """Return picture."""
# #     if 'username' in flask.session:
# #         return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
# #                                          filename, as_attachment=True)
# #     flask.abort(403)

# # @insta485.app.route('/accounts/login', methods=['GET', 'POST'])
# # def login():
# #     #need cookies, signed
# #     flask.session['username'] = flask.request.form['username']
# #     return flask.redirect(flask.url_for('show_index'))

@insta485.app.route('/')
def show_index():
    """Display / route."""


    # Connect to database
    connection = insta485.model.get_db()

    
    # Query database
    user = "awdeorio"
    cur = connection.execute(
        "SELECT postid, filename AS img_url, owner, created "
        "FROM posts "
        "WHERE owner = ? "

        # "UNION "

        # "SELECT username2 "
        # "FROM following "
        # "WHERE username1 = ?"

        # "SELECT postid, filename AS img_url, owner, created "
        # "FROM posts "
        # "WHERE owner = username2 "
    
        "ORDER BY postid DESC",
        (user, )
    )
    posts = cur.fetchall()
    for post in posts:
        # correct timestamp format
        post['timestamp'] = arrow.get(post['created']).humanize()

        # post's owner's icon url
        cur_owner = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (post['owner'], )
        )
        post['owner_img_url'] = cur_owner.fetchone()['filename']

        cur_comments = connection.execute(
            "SELECT postid, owner, text, created "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY created ASC",
            (post['postid'], )
        )
        comments = cur_comments.fetchall()
        for comment in comments:
            post['comments.owner'] = comment['owner']
            post['comments.text'] = comment['text']



    # Add database info to context
    context = {"posts": posts}
    return flask.render_template("index.html", **context)