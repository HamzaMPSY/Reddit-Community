import praw
import json
from datetime import datetime
import pymongo
from apscheduler.schedulers.blocking import BlockingScheduler
from config import *

"""
Grab data frmo SubReddit and Store it in MongoDB
1- get Articles and Comments the the user posted each Article/Comment
2- store Articles, Comments and Users in MongoDB
"""

# connect to local MongoDB
client = pymongo.MongoClient("mongodb", 27027)
redditdb = client.Reddit

def redditInstance():
	"""
		Connect to Reddit API using Cridentials in config.py
		return:
			praw.Reddit Instance
	"""
	assert len(CLIENT_ID) > 0
	return praw.Reddit(
		client_id = CLIENT_ID,
		client_secret = CLIENT_SECRET,
		user_agent = USERAGENT
		)


def cleanArticle(submission):
	"""
		take a Reddit submission object and turn it into dictionary
	"""
	now = datetime.utcnow()
	created = datetime.utcfromtimestamp(submission.created_utc)
	try:
		submission_author = submission.author.name
	except:
		submission_author = "None"

	data = {
			"article_id": submission.id, 
			"title": submission.title,
            "score": submission.score,
            "url": submission.url,
            "name": submission.name,
            "author": submission_author,
            "is_video": submission.is_video,
            "over_18": submission.over_18,
            "selftext": submission.selftext,
            "shortlink": submission.shortlink,
            "subreddit_type": submission.subreddit_type,
            "subreddit_subscribers": submission.subreddit_subscribers,
            "thumbnail": submission.thumbnail,
            "ups": submission.ups,
            "created_utc": created,
            "archived": now
	}
	return data


def cleanComment(comment,article_id):
	"""
		take a Reddit comment object and turn it into dictionary
	"""
	now = datetime.utcnow()
	created = datetime.utcfromtimestamp(comment.created_utc)

	try:
		name = comment.author.name
	except Exception as e:
		name = "None"

	data = {
		"comment_id": hash(comment.body),
		"article_id": article_id,
		"author": name,
		"body": comment.body,
		"ups": comment.ups,
		"created_utc" : created,
		"archived" : now
	}

	return data

def getRedditor(redditor):
	"""
		get a Redditor instance, and return useful information as dictionarry 
	"""
	now = datetime.utcnow()
	created = datetime.utcfromtimestamp(redditor.created_utc)

	data = {
		"redditor_id": redditor.id,
		"redditor_name" : redditor.name,
		"comment_karma" : redditor.comment_karma,
		"is_mod" : redditor.is_mod,
		"created_utc" : created,
		"archived": now
	}
	return data

def getArticlesCommentsUsers(subreddit,reddit):
	"""
		Function to (1) get the articles, comments and users from a subreddit, (2) store them in a mongoDB 
		
	"""

	all_submissions = [subreddit.top('hour'),subreddit.hot(),subreddit.rising()]
	for submissions in all_submissions:
		for submission in submissions:
			article = cleanArticle(submission)
			redditdb.Articles.insert(article)
			if article["author"] != 'None':
				user = getRedditor(reddit.redditor(article["author"]))
				redditdb.Users.insert(user)
			# to get all the comments and their replies 
			submission.comments.replace_more(limit=None)
			for comment in submission.comments.list():
				cmnt = cleanComment(comment,submission.id)
				redditdb.Comments.insert(cmnt)
				if cmnt["author"] != 'None':
					user = getRedditor(reddit.redditor(cmnt["author"]))
					redditdb.Users.insert(user)

def main():
	reddit = redditInstance()
	assert len(SUBREDDIT) > 0
	subreddit = reddit.subreddit(SUBREDDIT)
	getArticlesCommentsUsers(subreddit,reddit)

if __name__ == '__main__':
	main()
	scheduler = BlockingScheduler()
	scheduler.add_job(main, 'interval', hours=1)
	scheduler.start()