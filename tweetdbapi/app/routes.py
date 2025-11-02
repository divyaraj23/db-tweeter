from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import dbsetup

bp = Blueprint("api", __name__)


@bp.route("/refresh_token", methods=["POST"])
def api_refresh_token():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")

    if not username:
        return jsonify({"error": "username is required"}), 400

    return dbsetup.refresh_token(username)


@bp.route("/add_user", methods=["POST"])
def api_add_user():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")

    if not username:
        return jsonify({"error": "username is required"}), 400

    return dbsetup.create_user(username)


@bp.route("/add_tweet", methods=["POST"])
@jwt_required()
def api_add_tweet():
    payload = request.get_json(silent=True) or {}
    username = payload.get("uname")
    tweet_body = payload.get("tweetbody")

    if not username or tweet_body is None:
        return jsonify({"error": "uname and tweetbody are required"}), 400

    if username.lower() != get_jwt_identity():
        return jsonify({"error": "authentication failed"}), 401

    return dbsetup.create_tweet(payload)


@bp.route("/tweet_hist", methods=["POST"])
@jwt_required()
def api_tweet_hist():
    payload = request.get_json(silent=True) or {}
    username = payload.get("uname")
    if not username:
        return jsonify({"error": "uname is required"}), 400

    if username.lower() != get_jwt_identity():
        return jsonify({"error": "authentication failed"}), 401

    return dbsetup.get_tweets_not_older(payload)


@bp.route("/tweet_delete", methods=["DELETE"])
@jwt_required()
def api_tweet_delete():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "username query parameter is required"}), 400

    if username.lower() != get_jwt_identity():
        return jsonify({"error": "authentication failed"}), 401

    return dbsetup.delete_tweets_by_user(username)
    