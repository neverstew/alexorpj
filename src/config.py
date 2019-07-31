import os

from dotenv import load_dotenv
load_dotenv()

class Config(object):
    NUM_TWEETS=int(os.getenv('NUM_TWEETS', default=500))
    SECRET_KEY=os.getenv('SECRET_KEY')
    TWITTER_CONSUMER_TOKEN=os.getenv('TWITTER_CONSUMER_TOKEN')
    TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET')
