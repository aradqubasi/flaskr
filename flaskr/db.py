from pymongo import MongoClient
import click
from flask import current_app, g
from flask.cli import with_appcontext
import json
from pymongo.collection import Collection

class Dao:
    """ Data access class."""

    def __init__(self, host: str, database: str):
        """ Create new DAO atop of MongoClient"""
        self.client = MongoClient(host)
        self.database = database
        self.POSTS = "posts"
        self.USERS = "users"

    def get_default_query(self):
        return { "partition_id": 1 }

    def insert_posts(self, posts: [dict]):
        for post in posts:
            post.setdefault('partition_id', 1)  
        self.client                                 \
            .get_database(name=self.database)       \
            .get_collection(name=self.POSTS)        \
            .insert_many(posts)

    def insert_users(self, users: [dict]):
        for user in users:
            user.setdefault('partition_id', 1)
        self.client                                 \
            .get_database(name=self.database)       \
            .get_collection(name=self.USERS)        \
            .insert_many(users)
        # for user in users:
        #     print(user)
        #     self.client                                 \
        #         .get_database(name=self.database)       \
        #         .get_collection(name=self.USERS)        \
        #         .insert_one(user)              

    def select_user_by(self, username=None, userid=None):
        query = self.get_default_query()

        if username is not None:
            query['username'] = username

        if userid is not None:
            query['id'] = userid

        result = self.client                        \
            .get_database(name=self.database)       \
            .get_collection(name=self.USERS)        \
            .find_one(query)

        return result

    def delete_all_posts(self):
        self.client                                 \
            .get_database(name=self.database)       \
            .get_collection(self.POSTS)             \
            .delete_many(self.get_default_query())
        
    def delete_all_users(self):
        self.client                                 \
            .get_database(name=self.database)       \
            .get_collection(self.USERS)             \
            .delete_many(self.get_default_query())

    def close(self):
        self.client.close()


def get_db()->Dao:
    if 'db' not in g:
        g.db = Dao(current_app.config['CONNECTION_STRING'], current_app.config['DATABASE'])
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    # db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('initialization.json') as f:
        data = json.load(f)
        db.delete_all_posts()
        # db.insert_posts(data["posts"])
        db.delete_all_users()
        # db.insert_users(data["users"])

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    #click.echo('Initializing the database.')
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)