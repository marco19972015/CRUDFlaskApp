# Import the Flask class 
from flask import Flask, render_template, request

# When returning HTML (the defualt response type in Flask), any user-provided values rendered 
# in the out must be escaped to protext from injection attacks.
# HTML templates rendered with Jinja introduced later, will do this automatically.
from markupsafe import escape

# __name__ is needed so that Flask knows where to look for resources such as templates and static files
app = Flask(__name__)

# We use the route() decorator to tell Flask what URL should trigger our function
@app.route("/")
def index():
    return "Index Page"


@app.route('/user/<username>')
def show_user_profile(username):
    # Show the user profile for that user
    return f"User {escape(username)}"

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # Show the post with the given id, the id is an integer
    return f"Post {post_id}"

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f"Subpath {escape(subpath)}"

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)