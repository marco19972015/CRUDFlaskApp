# This file serves double duty: It will contain the application factory, and it tells
#  Python that the flaskr directoy should be treated as a package

import os
from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    # This line of code below creates the Flask instance
    # instance... tells the app that configuration files are relative to the instance folder
    # The instance folder is located outside the 'flaskr' package and can hold local data that shoudn't be committed to version control
    # such as configuration secrets and the database file
    app = Flask(__name__, instance_relative_config=True)  

    # app.config... sets some default configuration that the app will use
    app.config.from_mapping(
        # SECRET... is used by Flask and extensions to keep data safe
        SECRET_KEY='dev',
        # DATABASE is the path where SQLite database file will be saved. 
        # It's under app.instance..., which is the path that Flask has chosen for the instance folder
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    # 
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        # app.config... overrides the default configuration with values taken from the config.py file in the instance folder if it exists
        # For example, when deploying this can be used to set a real SECRET_KEY 
        app.config.from_pyfile('ocnfig.py', silent=True)
    else:
        # Load the test config if passed in 
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        # os... ensures that the app.instance_path exists. Flask doesn't create the instance folder automatically, but it needs to be 
        # created because our project will create the SQLite database file there 
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A simple page that says hello
    @app.route('/helloo')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)

    return app