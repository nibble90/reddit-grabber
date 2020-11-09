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
        self.uuids = []

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

    def write_cache(self, subreddit=None, title=None, score=None, url=None, selftext=None, author=None, post_id=None):
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
    
    def write_timestamps(self, post0=None, post1=None, post2=None, post3=None, post4=None, post5=None, post6=None, post7=None, post8=None, post9=None):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        unix_timestamp = self.unix_time()
        post0 = str(post0, )
        post1 = str(post1, )
        post2 = str(post2, )
        post3 = str(post3, )
        post4 = str(post4, )
        post5 = str(post5, )
        post6 = str(post6, )
        post7 = str(post7, )
        post8 = str(post8, )
        post9 = str(post9, )
        c.execute("INSERT INTO posts_cache(unix_timestamp, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (unix_timestamp, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9))
        connection.commit()
        connection.close()

    def grab_uuid(self, post_id=None):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        post_id = str(post_id, )
        c.execute("SELECT uuid FROM posts WHERE id=?", (post_id, ))
        result = c.fetchall()
        connection.commit()
        connection.close()
        return (result[0][0])

    def uuid_info(self, post_id):
        uuid = self.grab_uuid(post_id)
        self.uuids.append(uuid)

    def cache_into_timestamps(self):
        self.write_timestamps(self.uuids[0], self.uuids[1], self.uuids[2], self.uuids[3], self.uuids[4], self.uuids[5], self.uuids[6], self.uuids[7], self.uuids[8], self.uuids[9])


if __name__ == "__main__":
    pics = RedditAPI().pics()
    db = database()
    for title, score, url, selftext, author, post_id in pics:
        db.write_cache("pics", title, score, url, selftext, author, post_id)
        db.uuid_info(post_id)
    db.cache_into_timestamps()

