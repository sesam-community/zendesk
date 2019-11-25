import os
import tempfile

import pytest

from .. import zendesk-service

# https://flask.palletsprojects.com/en/1.1.x/testing/
# https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/

@pytest.fixture(scope='module')
def client():
    db_fd, zendesk-service.app.config['DATABASE'] = tempfile.mkstemp()
    zendesk-service.app.config['TESTING'] = True

    with zendesk-service.app.test_client() as client:
        with zendesk-service.app.app_context():
            pass
        yield client

    os.close(db_fd)
    os.unlink(zendesk-service.app.config['DATABASE'])

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('TESTING', "True")
    monkeypatch.setenv('DEBUG', "True")
