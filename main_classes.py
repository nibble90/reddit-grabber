import praw, sqlite3, time
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
        return_list = []
        for submission in subreddit_top:
            tuple_to_append = (submission.title, submission.score, submission.url, submission.selftext, submission.author, submission.id)
            return_list.append(tuple_to_append)
        return return_list

class database:
    def __init__(self, db="/home/ubuntu/jacobbot/reddit-grabber/posts.db"):
        self.db = db
        self.__create_databases()

    def __create_databases(self):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts
             (uuid INTEGER PRIMARY KEY AUTOINCREMENT, subreddit TEXT, title TEXT, score TEXT, url TEXT,
             selftext TEXT, author TEXT, id TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS posts_cache
             (uuid INTEGER PRIMARY KEY AUTOINCREMENT, unix_timestamp INTEGER, post0 TEXT, 
             post1 TEXT, post2 TEXT, post3 TEXT, post4 TEXT, post5 TEXT, post6 TEXT, 
             post7 TEXT, post8 TEXT, post9 TEXT, FOREIGN KEY(post0) REFERENCES posts(uuid), 
             FOREIGN KEY(post1) REFERENCES posts(uuid), FOREIGN KEY(post2) REFERENCES posts(uuid), FOREIGN KEY(post3) REFERENCES posts(uuid), 
             FOREIGN KEY(post4) REFERENCES posts(uuid), FOREIGN KEY(post5) REFERENCES posts(uuid), FOREIGN KEY(post6) REFERENCES posts(uuid), 
             FOREIGN KEY(post7) REFERENCES posts(uuid), FOREIGN KEY(post8) REFERENCES posts(uuid), FOREIGN KEY(post9) REFERENCES posts(uuid))''')
        connection.commit()
        connection.close()

    def unix_time(self):
        return int(time.time())

    def write_pics(self, subreddit=None, title=None, score=None, url=None, selftext=None, author=None, post_id=None):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        title = str(title, )
        score = str(score, )
        url = str(url, )
        selftext = str(selftext, )
        author = str(author, )
        post_id = str(post_id, )
        subreddit = str(subreddit, )
        c.execute("INSERT INTO posts(subreddit, title, score, url, selftext, author, id) VALUES(?, ?, ?, ?, ?, ?, ?)", 
            (subreddit, title, score, url, selftext, author, post_id))
        connection.commit()
        connection.close()


if __name__ == "__main__":
    pics = RedditAPI().pics()
    db = database()
    for title, score, url, selftext, author, post_id in pics:
        db.write_pics("pics", title, score, url, selftext, author, post_id)
