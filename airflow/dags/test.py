from datetime import datetime, timedelta
from pymongo import MongoClient
import time

# connect to local MongoDB
client = MongoClient("mongodb", 27017)
db = client.Reddit

def extractFromMongDB():
	"""Extracts all tweets from the MongoDB database as a list"""
	# define a timestamp to only extract newest data
	last_extraction_date = datetime.utcnow() - timedelta(minutes=1)
	articles = list(db.Articles.find({"archived": {"$gte": last_extraction_date}}))
	comments = list(db.Comments.find({"archived": {"$gte": last_extraction_date}}))
	users = list(db.Users.find({"archived": {"$gte": last_extraction_date}}))
	return [articles,comments,users]


while True:
	infos = extractFromMongDB()
	print(len(infos[0]),len(infos[1]),len(infos[2]))
	time.sleep(60)