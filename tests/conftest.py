import os
import json
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'rb') as f:
    _data_json = json.load(f)

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'dev',
        'CONNECTION_STRING': 'mongodb://py1:eI51iTn0rhfoncFM5h9inQ4WMTtwVwCOsnCT0CvYpKNBPAXF7rkqzRkM51WV7k6qiIkZEc4T35COQPODWmdIFw==@py1.documents.azure.com:10255/?ssl=true&replicaSet=globaldb',
        'DATABASE': 'dev' 
    })

    with app.app_context():
        init_db()
        db = get_db()
        db.insert_posts(_data_json['posts'])
        db.insert_users(_data_json['users'])

    yield app
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)