import praw
import json
import datetime
from config import *

"""
Grab data frmo SubReddit and Store it in MongoDB
1- get Articles and Comments the the user posted each Article/Comment
"""

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
	now = datetime.datetime.utcnow()
	created = datetime.datetime.utcfromtimestamp(submission.created_utc)
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
	now = datetime.datetime.utcnow()
	created = datetime.datetime.utcfromtimestamp(comment.created_utc)

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

def getArticlesComments(subreddit):
	"""
		Function to get the articles and comments from a subreddit
		return :
			articles : array of json blobs each one contains an article from the subreddit
			commnets : array of json blobs each one is a comment corresponding to an article in the articles array;
	"""
	comments = []
	articles = []
	submissions = subreddit.top('hour')
	for submission in submissions:
		articles.append(cleanArticle(submission))
		# to get all the comments and their replies 
		submission.comments.replace_more(limit=None)
		for comment in submission.comments.list():
			comments.append(cleanComment(comment,submission.id))

	return articles,comments

def getRedditor(redditor):
	"""
		get a Redditor instance, and return useful information as dictionarry 
	"""
	now = datetime.datetime.utcnow()
	created = datetime.datetime.utcfromtimestamp(redditor.created_utc)

	data = {
		"redditor_id": redditor.id,
		"redditor_name" : redditor.name,
		"comment_karma" : redditor.comment_karma,
		"is_mod" : redditor.is_mod,
		"created_utc" : created,
		"archived": now
	}
	return data

def main():
	reddit = redditInstance()
	assert len(SUBREDDIT) > 0
	subreddit = reddit.subreddit(SUBREDDIT)
	articles, comments = getArticlesComments(subreddit)
	redditors = []
	for article in articles:
		if article["author"] != 'None':
			redditors.append(getRedditor(reddit.redditor(article["author"] )))
	for comment in comments:
		if comment["author"] != 'None':
			redditors.append(getRedditor(reddit.redditor(article["author"] )))
	print(len(redditors),len(articles)+len(comments))

if __name__ == '__main__':
	main()