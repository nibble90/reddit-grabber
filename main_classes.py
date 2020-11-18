import praw, sqlite3, time, threading
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')
dir_path = path.dirname(path.realpath(__file__))
db_file_location = "{}/posts.db".format(dir_path)

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
            tuple_to_append = (submission.over_18, submission.title, submission.score, submission.url, submission.selftext, submission.author, submission.id)
            return_list.append(tuple_to_append)
        return return_list

    def subreddit_search(self, sub, override=False):
        subreddit_top = self.reddit.subreddit(sub).top("day", limit=10)
        return_list = []
        for submission in subreddit_top:
            tuple_to_append = (submission.over_18, submission.title, submission.score, submission.url, submission.selftext, submission.author, submission.id)
            return_list.append(tuple_to_append)
            if not override:
                db = database()
                db.add_custom_sub(submission.over_18, sub, submission.title, submission.score, submission.url, submission.selftext, submission.author, submission.id)
        if not override:
            db.cache_into_timestamps(sub)
        return return_list

class database:
    def __init__(self, db=db_file_location):
        self.db = db
        self.__create_databases()
        self.uuids = []
        self.reftime = time.time()
        self.reset_lock = False

    def __create_databases(self):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts
             (uuid INTEGER PRIMARY KEY AUTOINCREMENT, nsfw TEXT, subreddit TEXT, title TEXT, score TEXT, url TEXT,
             selftext TEXT, author TEXT, id TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS posts_cache
             (uuid INTEGER PRIMARY KEY AUTOINCREMENT, unix_timestamp INTEGER, subreddit TEXT, post0 TEXT, 
             post1 TEXT, post2 TEXT, post3 TEXT, post4 TEXT, post5 TEXT, post6 TEXT, 
             post7 TEXT, post8 TEXT, post9 TEXT, FOREIGN KEY(post0) REFERENCES posts(uuid), 
             FOREIGN KEY(post1) REFERENCES posts(uuid), FOREIGN KEY(post2) REFERENCES posts(uuid), FOREIGN KEY(post3) REFERENCES posts(uuid), 
             FOREIGN KEY(post4) REFERENCES posts(uuid), FOREIGN KEY(post5) REFERENCES posts(uuid), FOREIGN KEY(post6) REFERENCES posts(uuid), 
             FOREIGN KEY(post7) REFERENCES posts(uuid), FOREIGN KEY(post8) REFERENCES posts(uuid), FOREIGN KEY(post9) REFERENCES posts(uuid))''')
        connection.commit()
        connection.close()

    def __reset_database(self):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        c.execute('''DELETE FROM posts''')
        c.execute('''DELETE FROM posts_cache''')
        c.execute('''DELETE FROM SQLITE_SEQUENCE''')
        connection.commit()
        connection.close()
        self.uuids = []

    def begin_reset_loop(self):
        endtime = 120.0 - ((time.time() - self.reftime) % 60.0)
        threading.Timer(endtime, self.begin_reset_loop).start()
        self.reset_lock = True
        self.__reset_database()
        self.pics_run()
        self.aww_run()

    def begin_cache_refresh(self):
        endtime = 60.0 - ((time.time() - self.reftime) % 60.0)
        threading.Timer(endtime, self.begin_cache_refresh).start()
        if not self.reset_lock:
            self.refresh_cache()
        self.reset_lock = False

    def refresh_cache(self):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        c.execute('''SELECT subreddit, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9 FROM posts_cache''')
        results = c.fetchall()
        connection.commit()
        connection.close()

        for sub, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9 in results:
            if len(sub) > 1:
                result = RedditAPI().subreddit_search(sub)
                connection = sqlite3.connect(self.db)
                c = connection.cursor()

                list_of_posts = [post0, post1, post2, post3, post4, post5, post6, post7, post8, post9]

                for nsfw, title, score, url, selftext, author, post_id in result:
                    title = str(title, )
                    score = str(score, )
                    url = str(url, )
                    selftext = str(selftext, )
                    author = str(author, )
                    post_id = str(post_id, )
                    post = list_of_posts.pop(0)
                    c.execute('''UPDATE posts SET nsfw=?, title=?, score=?, url=?, selftext=?, author=?, id=? WHERE uuid=?''', (nsfw, title, score, url, selftext, author, post_id, post))
                connection.commit()
                connection.close()

                # refresh is not behaving, adding rows when it shouldnt

    def unix_time(self):
        return int(time.time())

    def write_cache(self, nsfw=None, subreddit=None, title=None, score=None, url=None, selftext=None, author=None, post_id=None):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        title = str(title, )
        score = str(score, )
        url = str(url, )
        selftext = str(selftext, )
        author = str(author, )
        post_id = str(post_id, )
        subreddit = str(subreddit, )
        c.execute("INSERT INTO posts(nsfw, subreddit, title, score, url, selftext, author, id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", 
            (nsfw, subreddit, title, score, url, selftext, author, post_id))
        connection.commit()
        connection.close()
    
    def write_timestamps(self, subreddit=None, post0=None, post1=None, post2=None, post3=None, post4=None, post5=None, post6=None, post7=None, post8=None, post9=None):
        connection = sqlite3.connect(self.db)
        c = connection.cursor()
        unix_timestamp = self.unix_time()
        subreddit = str(subreddit, )
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
        c.execute("INSERT INTO posts_cache(unix_timestamp, subreddit, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (unix_timestamp, subreddit, post0, post1, post2, post3, post4, post5, post6, post7, post8, post9))
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

    def cache_into_timestamps(self, subreddit):
        print(subreddit, self.uuids)
        self.write_timestamps(subreddit, self.uuids[0], self.uuids[1], self.uuids[2], self.uuids[3], self.uuids[4], self.uuids[5], self.uuids[6], self.uuids[7], self.uuids[8], self.uuids[9])

    def pics_run(self):
        content = RedditAPI().pics()
        db = database()
        print("printing content")
        print(*content)
        for nsfw, title, score, url, selftext, author, post_id in content:
            db.write_cache(nsfw, "pics", title, score, url, selftext, author, post_id)
            db.uuid_info(post_id)
            print(score, "post_id")
        db.cache_into_timestamps("pics")

    def aww_run(self):
        content = RedditAPI().subreddit_search("aww", override=True)
        db = database()
        for nsfw, title, score, url, selftext, author, post_id in content:
            db.write_cache(nsfw, "aww", title, score, url, selftext, author, post_id)
            db.uuid_info(post_id)
        db.cache_into_timestamps("aww")

    def add_custom_sub(self, nsfw, subreddit, title, score, url, selftext, author, post_id):
        db = database()
        db.write_cache(nsfw, subreddit, title, score, url, selftext, author, post_id)
        db.uuid_info(post_id)
        

if __name__ == "__main__":
    db = database()
    db.pics_run()
    db.aww_run()
    db.begin_reset_loop()
    db.begin_cache_refresh()
