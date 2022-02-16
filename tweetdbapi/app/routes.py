from flask import request, jsonify
from app import app,dbsetup

@app.route('/add_user', methods=['POST'])
def api_add_user():
    usr = request.get_json(force=True)
    return dbsetup.create_user(usr['username'])

@app.route('/add_tweet', methods=['POST'])
def api_add_tweet():
    twt = request.get_json(force=True)
    return dbsetup.create_tweet(twt)

@app.route('/tweet_hist', methods=['GET'])
def api_tweet_hist():
    twt = request.get_json(force=True)
    return dbsetup.get_tweets_not_older(twt)

@app.route('/tweet_delete', methods=['DELETE'])
def api_tweet_delete():
    usr = request.get_json(force=True)
    return dbsetup.delete_tweets_by_user(usr['username'])