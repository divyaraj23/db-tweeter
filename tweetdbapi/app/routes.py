from flask import request, jsonify, render_template
from app import app,dbsetup
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

@app.route('/refresh_token', methods=['POST'])
def api_refresh_token():
    user = request.get_json(force=True)
    return dbsetup.refresh_token(user['username'])

@app.route('/add_user', methods=['POST'])
def api_add_user():
    usr = request.get_json(force=True)
    print(usr)
    return dbsetup.create_user(usr['username'])
    

@app.route('/add_tweet', methods=['POST'])
@jwt_required()
def api_add_tweet():
    twt = request.get_json(force=True)
    if twt['uname'].lower() == get_jwt_identity():
        return dbsetup.create_tweet(twt)
    else:
        return jsonify("Authentication Failed")

@app.route('/tweet_hist', methods=['POST'])
@jwt_required()
def api_tweet_hist():
    twt = request.get_json(force=True)
    if twt['uname'].lower() == get_jwt_identity():
        return dbsetup.get_tweets_not_older(twt)
    else:
        return jsonify("Authentication Failed")
    

@app.route('/tweet_delete', methods=['DELETE'])
@jwt_required()
def api_tweet_delete():
    usr = request.args.get('username')
    if usr.lower() == get_jwt_identity():
        return dbsetup.delete_tweets_by_user(usr)
    else:
        return jsonify("Authentication Failed")
    