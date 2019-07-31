from flask import flash, Flask, redirect, render_template, request, url_for
from sklearn.feature_extraction.text import TfidfVectorizer

import functools
import os
import tweepy 

app = Flask(__name__)
app.config.from_object('config.Config')

def get_twitter_client():
    auth = tweepy.AppAuthHandler(
            app.config['TWITTER_CONSUMER_TOKEN'],
            app.config['TWITTER_CONSUMER_SECRET']
    ) 
    return tweepy.API(auth)

twitter = get_twitter_client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare')
def compare():
    # TODO: reject when silly user_id
    if 'user_id' not in request.args:
        flash('Please supply a twitter handle')
        return redirect(url_for('index'))
    user_id = request.args['user_id']
    
    # TODO: reject when too many requests

    print('Getting tweets for Alex...')
    alex_tweets = concat_tweets([tweet.text for tweet in tweepy.Cursor(twitter.user_timeline, id='agoldmund').items(app.config['NUM_TWEETS'])])
    print('Getting tweets for PJ...')
    pj_tweets = concat_tweets([tweet.text for tweet in tweepy.Cursor(twitter.user_timeline, id='pjvogt').items(app.config['NUM_TWEETS'])])
    print(f"Getting tweets for {user_id}...")
    user_tweets = concat_tweets([tweet.text for tweet in tweepy.Cursor(twitter.user_timeline, id=user_id).items(app.config['NUM_TWEETS'])])

    tfidf = TfidfVectorizer().fit_transform([alex_tweets, pj_tweets, user_tweets])
    similarity = tfidf * tfidf.T

    result_alex = similarity[2,0].round(3)*100
    result_pj = similarity[2,1].round(3)*100
    if result_alex > result_pj:
        result = "You're an Alex!"
    else:
        result = "You're a PJ!"

    return render_template('compare.html',
            handle = user_id,
            result = result,
            result_alex = result_alex,
            result_pj = result_pj
    )
 
def concat_tweets(tweets):
    import functools
    return functools.reduce(lambda a,b: f"{a} {b}", tweets)
