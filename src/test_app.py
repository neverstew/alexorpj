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

@patch('app.get_twitter_client')
@patch('tweepy.Cursor')
def test_should_return_comparison_results(mock_cursor, mock_twitter, client):
    class StubTweet(object):
        def __init__(self, text):
            self.text = text
    
    mock_twitter.return_value.user_timeline = 'test thing'
    
    mock_cursor.return_value.items.side_effect = [
            [StubTweet('first alex'), StubTweet('second alex')],
            [StubTweet('first pj'), StubTweet('second pj')],
            [StubTweet('first bigboii'), StubTweet('second pj')]
    ]
    
    res = client.get('/compare?user_id=bigboii')
    assert 3 == mock_cursor.call_count
    assert b"You&#39;re a PJ!" in res.data 

def test_should_reduce_tweet_list():
    actual = ["First", "Second with more words", "Third! £%*^(", "4"]
    expected = "First Second with more words Third! £%*^( 4"

    assert expected == app.concat_tweets(actual)
