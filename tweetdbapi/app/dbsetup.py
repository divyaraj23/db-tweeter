from flask import jsonify
from app import db,ma
from sqlalchemy import func
import uuid
import datetime

class Users(db.Model):
    __tablename__ = 'users'
    '''
    Columns:
    1. user_id
    2. username
    3. created_timestamp

    '''
    user_id = db.Column(db.String(8),primary_key=True)
    username = db.Column(db.String(15))
    created_timestamp = db.Column(db.DateTime)

    def __init__(self, user_id, username, created_timestamp):
        self.user_id = user_id
        self.username = username
        self.created_timestamp = created_timestamp

class TweetData(db.Model):
    __tablename__ = 'tweetdata'
    '''
    Columns:
    1. tweet_id
    2. user_id
    3. tweet_text
    4. created_timestamp

    '''
    tweet_id = db.Column(db.String(50), primary_key = True)
    user_id = db.Column(db.String(8))
    tweet_text = db.Column(db.String(280))
    created_timestamp = db.Column(db.DateTime)

    def __init__(self, tweet_id, user_id, tweet_text, created_timestamp):
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.tweet_text = tweet_text
        self.created_timestamp = created_timestamp

db.create_all()

def create_user(user_name):
    # Check if username exists
    fetch_user = Users.query.filter_by(username = user_name.lower()).first()

    if fetch_user:
        return "Username already exists"
    else:
        currentDateTime = datetime.datetime.now()
        us_id = user_name[:6] + str(uuid.uuid4()
        .hex[:6])
        add_user = Users(us_id, user_name.lower(), currentDateTime)
        db.session.add(add_user)
        db.session.commit()
        return jsonify(user_id = us_id,
                        username = user_name)

def create_tweet(tweet_load):

    if len(tweet_load['tweetbody']) > 1 and len(tweet_load['tweetbody']) < 141:
        currentDateTime = datetime.datetime.now()
        fetch_user = Users.query.filter_by(username = tweet_load['uname'].lower()).first()
        if fetch_user.user_id:
            twid = str(uuid.uuid4())
            add_tweet = TweetData(twid , fetch_user.user_id, tweet_load['tweetbody'], currentDateTime)
            db.session.add(add_tweet)
            db.session.commit()
            return jsonify(tweet_id = twid,
                            created_timestamp = currentDateTime)
        else:
            return "User does not exist"
    else:
        return "Tweet length should be between 2 and 140 charachters"

def get_tweets_not_older(datenuser):
    fetch_user = Users.query.filter_by(username = datenuser['uname'].lower()).first()

    if fetch_user:
        entereddate = datetime.datetime.strptime(datenuser['grtndate'], "%d/%m/%Y").date()
        twts_nod = TweetData.query.filter(TweetData.user_id == fetch_user.user_id, TweetData.created_timestamp >= entereddate).all()
        
        if len(twts_nod)>0:
            twt_str = ""
            for items in twts_nod:
                if len(twt_str) == 0:
                    twt_str = twt_str+str(items.tweet_text)
                else:
                    twt_str = twt_str+','+str(items.tweet_text)

            return jsonify(numoftweets = str(len(twts_nod)),
                        tweets = twt_str)
        else:
            return "tweets not found"
    else:
        return "user not found"

def delete_tweets_by_user(user_name):
    fetch_user = Users.query.filter_by(username = user_name.lower()).first()

    if fetch_user:
        twts_to_del = TweetData.query.filter_by(user_id = fetch_user.user_id).all()
        
        if len(twts_to_del)>0:
            twt_str = ""
            for items in twts_to_del:
                if len(twt_str) == 0:
                    twt_str = twt_str+str(items.tweet_id)+'::'+str(items.tweet_text)
                else:
                    twt_str = twt_str+','+str(items.tweet_id)+'::'+str(items.tweet_text)
                db.session.delete(items)
                db.session.commit()
            
            return jsonify(numoftweets = str(len(twts_to_del)),
                        tweets_id_text = twt_str)
        else:
            return "tweets not found"
    else:
        return "user not found"
