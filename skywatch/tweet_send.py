
import os
import logging
import tweepy
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

load_dotenv()


class Tweet_Send():

    def __init__(self):

        X_API_KEY = os.getenv('X_API_KEY', None)
        X_API_SECRET = os.getenv('X_API_SECRET', None)
        X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN', None)
        X_ACCESS_SECRET = os.getenv('X_ACCESS_SECRET', None)

        # Authenticate
        auth = tweepy.OAuth1UserHandler(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
        self.api = tweepy.API(auth)


    def tweet_text(self, text):

        try:
            status = self.api.update_status(text)
        except Exception as e:
            print("Error tweeting:", e)
