# Import the database
import sqlite3

import click 

# g is a special object that is unique for each request. It's function is to store data that might be 
# accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if
# get_db is called a second time in the same request

# current_app is another special object that points to the Flask application handling the request
# Since we used application factory, there is no application object when writing the rest of the code.
# get_db function will be called when the application has been created and is handling a request, current_app can be used
from flask import current_app, g

def get_db():
    if 'db' not in g:
        # sqlite3... establishes a connection to the file pointed at by the DATABASE config key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.row tells the connection to return rows that behave like dictionaries. This allows accessing the columns by name
        g.db.row_factory = sqlite3.Row

        return g.db
    
def init_db():
    db = get_db()
    # Open_resources() opens a file relative to the flsakr package, which is useful since we wont necessarily know
    # where that location is when deploying the application later. get_db function returns a database connection, which is 
    # used to execute the commands read from the file
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() function defines a command line command called init-db that calls the init_db function and shows
# a success mesasge to the user. 
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database')

# REGISTER WITH THE APPLICATION
    # The close_db and init_db_command functions need to be registered with the application instance;
    # otherwise, they won't be used by the application. However, sinec we are using a factory function, 
    # that instance isn't available when writing the function. Instead, we write a function that takes in an application and does the registration
def init_app(app):
    # teardown... function tells Flask to call that function when cleaning up after returning the response
    app.teardown_appcontext(close_db)
    # cli... function adds a new command that can be called with the flask command
    app.cli.add_command(init_db_command)
    
# close_db function checks if a connection was created by checking if g.db was set. If the connection exists, it is closed.
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()