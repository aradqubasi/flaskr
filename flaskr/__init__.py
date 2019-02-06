import os

from flask import Flask


def create_app(test_config=None)->Flask:
    #create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        CONNECTION_STRING='mongodb://py1:eI51iTn0rhfoncFM5h9inQ4WMTtwVwCOsnCT0CvYpKNBPAXF7rkqzRkM51WV7k6qiIkZEc4T35COQPODWmdIFw==@py1.documents.azure.com:10255/?ssl=true&replicaSet=globaldb',
        DATABASE='dev'    
    )

    if test_config is None:
        #load the instance config, if it exists, if not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except:
        pass
    
    #a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World'
    
    from . import db
    db.init_app(app)

    @app.route('/create_tables')
    def create_tables():
        result = None
        database = db.get_db()
        with app.open_resource('schema.sql') as f:
            database.executescript(f.read().decode('utf8'))
            result = 'Done'
        if result is None:
            result = 'Failure'
        return result

    @app.route('/get_environment_variable/<variable_name>')
    def get_environment_variable(variable_name: str):
        result = os.environ[variable_name]
        return result

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app