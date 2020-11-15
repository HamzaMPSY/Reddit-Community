from datetime import datetime, timedelta
from pymongo import MongoClient
from sqlalchemy import text
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from config import *

# connect to local MongoDB
client = MongoClient("mongodb", 27017)
db = client.Reddit

# connect to postgres
conns = f"postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB_NAME}"
postgres_db = create_engine = create_engine(conns, encoding="utf-8")

# run initial queries
postgres_db.execute(CREATE_USERS_TABLE)
postgres_db.execute(CREATE_ARTICLES_TABLE)
postgres_db.execute(CREATE_COMMENTS_TABLE)


def extractFromMongDB():
	"""Extracts all tweets from the MongoDB database as a list"""
	# define a timestamp to only extract newest data
	last_extraction_date = datetime.utcnow() - timedelta(minutes=1)
	articles = list(db.Articles.find({"archived": {"$gte": last_extraction_date}}))
	comments = list(db.Comments.find({"archived": {"$gte": last_extraction_date}}))
	users = list(db.Users.find({"archived": {"$gte": last_extraction_date}}))

	return [articles,comments,users]

def loadInPostgres(**context):
	# extract data from context
	extract_connection = context["ti"]
	infos = extract_connection.xcom_pull(task_ids="extract")
	articles = infos[0]
	comments = infos[1]
	users = infos[2]

	for user in users:
		try :
			postgres_db.execute(
				text(INSERT_USER),
				{
					"redditor_id": user["redditor_id"],
					"redditor_name": user["redditor_name"],
					"comment_karma": user["comment_karma"],
					"is_mod": user["is_mod"],
					"created_utc": user["created_utc"],
					"archived": user["archived"]
				},
			)
		except :
			pass

	for article in articles:
		try:
			postgres_db.execute(
				text(INSERT_ARTICLE),
				{
					"article_id" : article["article_id"],
					"title" : article["title"],
					"score" : article["score"],
					"url" : article["url"],
					"name" : article["name"],
					"author" : article["author"],
					"is_video" : article["is_video"],
					"over_18" : article["over_18"],
					"selftext" : article["selftext"],
					"shortlink" : article["shortlink"],
					"subreddit_type" : article["subreddit_type"],
					"subreddit_subscribers" : article["subreddit_subscribers"],
					"thumbnail" : article["thumbnail"],
					"ups" : article["ups"],
					"created_utc" : article["created_utc"],
					"archived" : article["archived"]
				},
			)
		except:
			pass

	for comment in comments:
		try:
			postgres_db.execute(
				text(INSERT_COMMENT),
				{
				"comment_id" : comment["comment_id"],
				"article_id" : comment["article_id"],
				"author": comment["author"],
				"body": comment["body"],
				"ups": comment["ups"],
				"created_utc": comment["created_utc"],
				"archived": comment["archived"]
				}
			)
		except :
			pass

# define default arguments
default_args = {
    "owner": "MPSY",
    "start_date": datetime(2020, 11, 14),
    # 'end_date':
    "email": ["example@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# instantiate a DAG
dag = DAG(
    "RedditCommunity",
    description="",
    catchup=False,
    schedule_interval=timedelta(minutes=1),
    default_args=default_args,
)

# define tasks
t1 = PythonOperator(task_id="extract", python_callable=extractFromMongDB, dag=dag)

t2 = PythonOperator(task_id="load", provide_context=True, python_callable=loadInPostgres, dag=dag)

t1 >> t2