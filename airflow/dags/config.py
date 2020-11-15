# set parameters for local postgresDB
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_HOST = "postgresdb"
DATABASE_PORT = "5432"
DATABASE_DB_NAME = "postgres"

# create table for twitter data from mongodb
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    	redditor_id VARCHAR(50) PRIMARY KEY,
		redditor_name VARCHAR(150) UNIQUE NOT NULL,
		comment_karma INT NOT NULL,
		is_mod BOOLEAN NOT NULL,
		created_utc TIMESTAMP NOT NULL,
		archived TIMESTAMP NOT NULL
);
"""

CREATE_ARTICLES_TABLE = """
CREATE TABLE IF NOT EXISTS articles (
	article_id VARCHAR(50) PRIMARY KEY, 
	title VARCHAR(255) NOT NULL,
	score INT NOT NULL,
	url VARCHAR(255) NOT NULL,
	name TEXT NOT NULL,
	author VARCHAR(150) NOT NULL,
	is_video BOOLEAN NOT NULL,
	over_18 BOOLEAN NOT NULL,
	selftext TEXT NOT NULL,
	shortlink VARCHAR(255) NOT NULL,
	subreddit_type VARCHAR(50) NOT NULL,
	subreddit_subscribers INT NOT NULL,
	thumbnail VARCHAR(255) NOT NULL,
	ups INT NOT NULL,
	created_utc TIMESTAMP NOT NULL,
	archived TIMESTAMP NOT NULL,
	FOREIGN KEY (author) REFERENCES users (redditor_name)
);
"""

CREATE_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS comments (
	comment_id VARCHAR(50) PRIMARY KEY,
	article_id VARCHAR(50) NOT NULL,
	author VARCHAR(150) NOT NULL,
	body TEXT NOT NULL,
	ups INT NOT NULL,
	created_utc TIMESTAMP NOT NULL,
	archived TIMESTAMP NOT NULL,
	FOREIGN KEY (author) REFERENCES users (redditor_name),
	FOREIGN KEY (article_id) REFERENCES articles (article_id)
);
"""

INSERT_USER = """
INSERT INTO users VALUES (
    :redditor_id,
	:redditor_name,
	:comment_karma,
	:is_mod,
	:created_utc,
	:archived
);"""

INSERT_ARTICLE = """
INSERT INTO articles VALUES (
    :article_id, 
	:title,
	:score,
	:url,
	:name,
	:author,
	:is_video,
	:over_18,
	:selftext,
	:shortlink,
	:subreddit_type,
	:subreddit_subscribers,
	:thumbnail,
	:ups,
	:created_utc,
	:archived
);"""

INSERT_COMMENT = """
INSERT INTO comments VALUES (
    :comment_id,
	:article_id,
	:author,
	:body,
	:ups,
	:created_utc,
	:archived
);"""