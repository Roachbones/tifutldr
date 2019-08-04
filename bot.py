import praw
import tweepy
import re
from pprint import pprint
import json
import time

with open("keys.txt", "r") as file:
    keys = file.read().split("\n")

reddit = praw.Reddit(
    client_id=keys[0],
    client_secret=keys[1],
    user_agent="python:tifutldr:1.1 (by /u/amethystMushroom)"
)

CONSUMER_KEY = keys[2]
CONSUMER_SECRET = keys[3]
ACCESS_KEY = keys[4]
ACCESS_SECRET = keys[5]
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
twitter = tweepy.API(auth)

SUBNAME = "TIFU"
LOGFILE = "log.json"
TLDRPATTERN = "tl ?;?dr[ -:;>,]*(.*)"
MAXLEN = 280
DELAY = int(60 * 60 * 22) #every 22 hours

def getlog():
    with open(LOGFILE, "r", encoding="utf-8") as logfile:
        return json.load(logfile)

def hastwote(redditid):
    for entry in getlog():
        if entry["redditid"] == redditid:
            return True
    return False

def logtweet(tldr, tweetid):
    logjson = getlog()
    with open(LOGFILE, "w", encoding="utf-8") as logfile:
        entry = {
            "redditid": tldr["id"],
            "tweetid": tweetid,
            "tldrtext": tldr["text"],
            "time": time.time()
        }
        logjson.append(entry)
        json.dump(logjson, logfile)

def gettldrs():
    tldrs = []
    for s in reddit.subreddit(SUBNAME).hot(limit=16):
        #pprint(s.title)
        match = re.search(TLDRPATTERN, s.selftext, re.I)
        if match and match.group(1):
            tldr = {
                'text': match.group(1),
                'id': s.id
            }
            if not (
                tldr["text"].startswith("at the end") or
                tldr["text"].startswith("at the bottom")
            ):
                tldrs.append(tldr)
    return tldrs

def main():
    for tldr in gettldrs():
        if hastwote(tldr["id"]):
            print("not tweeting; already twote :P")
            print(tldr)
            continue
        try:
            tweetid = twitter.update_status(tldr["text"][:MAXLEN]).id_str
            print("twote :3")
            print(tldr)
        except:
            print("twitter error XnX")
            print(tldr)
            continue
        logtweet(tldr, tweetid)
        time.sleep(DELAY)
    time.sleep(DELAY)
while 1:
    main()
