from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)
# After the code is written above we need to import and register this blueprint in app.register_blueprint()

@bp.route('/')
def index():
    db = get_db()
    # In this query below I'm getting the posts for a specific user
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    # Render the template and have the variable posts be passed to the template
    return render_template('blog/index.html', posts=posts)

# route for create path
@bp.route('/create', methods=('GET', 'POST'))
# When using this decorator here, Flask will ensure that the current user is logged in and authenticated
# before calling the actual view. (If they are not, it calls the LoginManager.unauthorized callback)
@login_required
def create():
    if request.method == 'POST':
        # Retrieve data from form
        title = request.form['title']
        body = request.form['body']
        error = None
        
        # Validation
        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            # insert new blog post with the title, body, and author_id
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            # commit query
            db.commit()
            # Have the user be redirected to blog.index
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')


# UPDATE
# Both the update and delete views will need to fetch a post by id and check if the author matches the logged in user.
# To avoid duplication code, we can write a function to get the post and call it from each view

#  The check_authoer argument is defined so the function can be used to get a POST without checking the author.
# This is useful in we wrote a view to show an inidividual post on a page, where the user doesn't matter because they're not modifying the post 
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone

    # Below abort() will raise a special exception that returns an HTTP status code. It takes an optional message to show with 
    # the error, otherwise a default message is used. 404 not found, 401 Unauthorized
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

#  A real URL will look like /1/update. Flask will capture the 1, ensure it's an int, and pass it as the id argument.
#  If we don't specify int: and instead do <id>, it will be a string
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
# To generate a URL to the update page, url_for() needs to be passed the id so it knows 
# what to fill in: url_for('blog.update', id=post...). 
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)

# DELETE view
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id))
    db.commit()
    return redirect(url_for('blog.index'))

# SIDE NOTES. 
# With some refractoring, I could use one view and template for both the create and update view