"""
Insta485 accounts view.


URLs include:
/accounts/login/
/accounts/logout/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import uuid
import hashlib
import insta485

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

@insta485.app.route('/accounts/create', methods=['GET'])
def create_account():
    #TODO: ALL OF IT
    return render_template("login.html")

@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """All /accounts/ POST requests"""
    # TODO Confused by what it means 'redirect to URL' after completeing action
    operation = request.values.get('operation')
    if operation is "login":
        login()
    
    else:
        return redirect(url_for('show_index'))
    
    # Redirect to what target arg equals in URL
    target = request.args.get('target')
    return redirect(target)