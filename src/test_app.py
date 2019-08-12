from freezegun import freeze_time
from unittest.mock import patch

import app
import datetime
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
            # first time called
            [StubTweet('first alex'), StubTweet('second alex')],
            [StubTweet('first pj'), StubTweet('second pj')],
            [StubTweet('first bigboii'), StubTweet('second pj')],
            # second time alex and pj cached
            [StubTweet('first bigboii'), StubTweet('second pj')],
            # third time called again
            [StubTweet('third alex'), StubTweet('fourth alex')],
            [StubTweet('third pj'), StubTweet('fourth pj')],
            [StubTweet('first bigboii'), StubTweet('second pj')]
    ]
    
    with freeze_time('2019-9-12'):
        res = client.get('/compare?user_id=bigboii')
        assert 3 == mock_cursor.call_count
        assert b"You&#39;re a PJ!" in res.data 

        # ensure comparison form in response page
        assert b'form' in res.data
        assert b'action="/compare"' in res.data
        assert b'placeholder="twitter handle"' in res.data

        assert 'agoldmund' in app.fetched_tweets
        assert app.fetched_tweets['agoldmund'] == 'first alex second alex'
        assert app.last_fetched['agoldmund'] == datetime.datetime(2019,9,12)
        assert 'pjvogt' in app.fetched_tweets
        assert app.fetched_tweets['pjvogt'] == 'first pj second pj'
        assert app.last_fetched['pjvogt'] == datetime.datetime(2019,9,12)
        assert 'bigboii' not in app.fetched_tweets

        res = client.get('/compare?user_id=bigboii')
        # results for alex and pj should have cached since we just grabbed 
        # the tweets for this user
        assert 4 == mock_cursor.call_count

    with freeze_time('2019-9-14'):
        res = client.get('/compare?user_id=bigboii')
        # cache out of time so should be called again
        assert 7 == mock_cursor.call_count
        assert app.fetched_tweets['agoldmund'] == 'third alex fourth alex'
        assert app.last_fetched['agoldmund'] == datetime.datetime(2019,9,14)


def test_should_reduce_tweet_list():
    actual = ["First", "Second with more words", "Third! £%*^(", "4"]
    expected = "First Second with more words Third! £%*^( 4"

    assert expected == app.concat_tweets(actual)

def test_should_reduce_empty_tweet_list_to_empty_string():
    actual = []
    expected = ""

    assert expected == app.concat_tweets(actual)

def test_recently_fetched():
    # should return false when not fetched before
    assert not app.recently_fetched('tester')
    # should return true when fetched in last day
    app.last_fetched['tester'] = datetime.datetime(year=2019, month=9, day=12)
    assert app.recently_fetched('tester')
    # should return false when fetched over a day ago
    with freeze_time('2019-9-14'):
        assert not app.recently_fetched('tester')
