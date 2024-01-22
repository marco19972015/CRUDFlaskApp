# A Blueprint is a way to organize a group of related views and other code. Rather than registering views and other code
# directly with an application, they are registered with a blueprint. Then the blueprint is registered with the application 
# when it is available in the factory function

# Flaskr will have two blueprints, one for authentication functions and one for the blog posts functions. The code for each 
# blueprint will go in a separate module.

import functools

# url_for - a function that enables us to build and generate URLs on a Flask application
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# This creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it's defined, so 
# __name__ is passed as the second argument. The url_prefix will be prepended to all the URLs associated with the blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route associates the URL /register with the register view function. When Flask receives a request to /auth/register, 
# it will call the register view and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # request.form is a special type of dict mapping submitted form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # Validate the username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required'

        # If validation is successful
        if error is None:
            try:
                # Take the SQL query with ? placeholders for any user input, and a tuple of values to replace the placeholders with
                db.execute(
                    # The ? are placeholders to the variables 
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    # gen_has is used to securely hash the password
                    (username, generate_password_hash(password)),
                )
                # After above code is executed we commit the query
                db.commit()
            # an sqlite3.IntegrityError will occur if the username already exists, which should be shown to the user an another validation error
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # after user is stored, redirect user to login page. url_for() generates the URL for the login view based on its name.
                # This is preferable to writing the URL directly as it allows us to change the URL later wihtout ALL code that links to it
                return redirect(url_for("auth.login"))
        # If validation faild, the error is shown to the user. flash() stores messages that can be retrieved when rendering the template
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # user is queried first and stored in a variable for later use
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        # fetchone() returns one row from the query. If the query returned no results, it returns None
        # Later, fetchall() will be used, which returns a list of all results
        ).fetchone() 

        if user is None:
            error = 'Incorrect username.'
        # check_password... hashes the submitted password in the same way as the stored hash and securely compares them. If they match 
        # the password is valid
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests. When validation succeeds, the user's id is stored in a new session. 
            # The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent request. 
            # Flask securely signs the data so that it can't be tampered with.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        # Now that the user's id is stored in the session, it will be available on subsequent requests.
        # At the biginning of each request, if a user is logged in their information should be loaded and made available to other views
        
        flash(error)

    return render_template('auth/login.html')

# bp.before... registers a function that runs before the view function, no matter what URL is requested. 
@bp.before_app_request
# load_logged... checks if a user is stored in the session and gets the user's data from the database, storing it on g.user, which
# lasts for the length of the request. If there is no user id, or if the id doesn't exist, g.user will be None
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Logout
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Require Authentication in other views 
# Creating, editing, and deleting blog posts will require a user to be logged in. 
# A decorator can be used to check this for each view it's applied to.
def login_required(view):
    # This decorator returns a new view function that wraps the original view it's applied to
    @functools.wraps(view)
    # The new function checks if a user is loaded and redirects to the login page 
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        # Otherwise, if a user is loaded the original view is called and continues normally 
        return view(**kwargs)
    
    return wrapped_view
