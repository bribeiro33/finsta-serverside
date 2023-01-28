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
import pathlib
import hashlib
import insta485

# ============================ Login/out ===================================
@insta485.app.route('/accounts/login/', methods=["GET"])
def login_page():
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

# Can't be in post_accounts because no target arg
@insta485.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """POST logout of account request"""
    user = session.get('user')
    
    # Error somehwere if user is not logged in here, safety
    # Clears cookies
    if user:
        session.clear()
        
    return redirect(url_for('login_page'))

# ============================ Create =====================================
# Renders the create an account page, redirect to edit if logged in
@insta485.app.route('/accounts/create', methods=['GET'])
def create_page():
    """GET create account page"""
    if "user" in session:
        redirect(url_for('edit.html'))
    return render_template('create.html') 

def create_account():
    """POST created account"""
    # Get information from form on create page
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['fullname']
    email = request.form['email']
    file_obj = request.files['file']

    # If something hasn't been filled out, abort
    if not(username and password and full_name and email and file_obj):
        abort(400)
    
    # If username already exists, abort
    connection = insta485.model.get_db()
    cur_users = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == ?",
        (username, )
    )
    if cur_users.fetchone():
        abort(409)

    # Hash password to store securley
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # Convert file into appropriate format
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
        "users(username, fullname, email, filename, password) "
        " VALUES (?,?,?,?,?)",
        (username, full_name, email, filename, password_db_string, )
    )

    # Log new user in, set session cookie
    session['user'] = username

# ============================ Edit =====================================
# Renders the edit your account page, redirect to edit if logged in
@insta485.app.route('/accounts/edit', methods=['GET'])
def edit_page():
    """GET edit account page"""
    # Query db for logged in user's current info
    connection = insta485.model.get_db()
    cur_user = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users "
        "WHERE username == ?",
        (session['user'], )
    )
    user_profile = cur_user.fetchone()
    if not user_profile:
        abort(403)
    
    # Fix file path to work w/ flask
    user_profile['filename'] = flask.url_for("file_url", filename=user_profile['filename'])

    context = {"user": user_profile}
    return render_template('edit.html', **context)

def edit_account():
    """POST edits to user's account"""
    if "user" not in session: 
        abort(403)
    

# Various post requests from accounts with operation values 
@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """All /accounts/?target= POST requests"""
    operation = request.values.get('operation')
    if operation == "login":
        login()
    elif operation == "create":
        create_account()
    elif operation == "edit_account":
        edit_account()
    else:
        return redirect(url_for('show_index'))
    
    # Redirect to what target arg equals in URL
    target = request.args.get('target')
    return redirect(target)