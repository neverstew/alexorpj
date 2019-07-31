from unittest.mock import patch

import app
import pytest


@pytest.fixture
def client():
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        yield client

def test_app_loads(client):
    res = client.get('/')
    
    assert 200 == res.status_code
    assert b'Alex or PJ?' in res.data

    assert b'form method="get" action="/compare"' in res.data

def test_should_redirect_compare_when_no_user_id(client):
    res = client.get('/compare', follow_redirects=True)

    assert b'Please supply a twitter handle' in res.data

@patch('tweepy.API')
@patch('tweepy.AppAuthHandler')
def test_should_setup_twitter_api(mock_auth, mock_api):
    app.app.config['TWITTER_CONSUMER_TOKEN'] = 'test_token'
    app.app.config['TWITTER_CONSUMER_SECRET'] = 'test_secret'

    twitter = app.get_twitter_client()
        
    mock_auth.assert_called_once_with('test_token', 'test_secret')
    mock_api.assert_called_once_with(mock_auth())
