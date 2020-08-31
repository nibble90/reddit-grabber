import praw
from os import getenv
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')

class RedditAPI:
    def __init__(self):
        self.reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent="JacobBot Reddit Grabber (admin is u/nibble90)")

    #Will not work, grabbing top 10 may not trigger limits?
    def rate_check(self):
        return praw.models.Auth(self.reddit, None).limits

    def pics(self):
        subreddit_top = self.reddit.subreddit("pics").top("day", limit=10)
        for submission in subreddit_top:
            return (submission.title, submission.score, submission.url)

if __name__ == "__main__":
    RedditAPI().pics()
