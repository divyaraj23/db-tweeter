import datetime
import uuid
from typing import Dict, Iterable, List

from flask import jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import delete, select

from app import db


class Users(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(8), primary_key=True)
    username = db.Column(db.String(15), unique=True, index=True, nullable=False)
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    tweets = db.relationship("TweetData", backref="user", lazy="dynamic")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Users user_id={self.user_id} username={self.username}>"


class TweetData(db.Model):
    __tablename__ = "tweetdata"

    tweet_id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(8), db.ForeignKey("users.user_id"), nullable=False, index=True)
    tweet_text = db.Column(db.String(280), nullable=False)
    created_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<TweetData tweet_id={self.tweet_id} user_id={self.user_id}>"


def _normalize_username(user_name: str) -> str:
    return (user_name or "").strip().lower()


def _generate_user_id(username: str) -> str:
    prefix = (username[:2] or "us").ljust(2, "x")
    return f"{prefix}{uuid.uuid4().hex[:6]}"


def _display_username(user_name: str, normalized: str) -> str:
    return (user_name or "").strip() or normalized


def refresh_token(user_name: str):
    username = _normalize_username(user_name)

    if not username:
        return jsonify({"error": "username is required"}), 400

    fetch_user = Users.query.filter_by(username=username).first()

    if not fetch_user:
        return jsonify({"error": "user not found"}), 404

    access_token = create_access_token(identity=fetch_user.username)
    return jsonify({
        "username": _display_username(user_name, fetch_user.username),
        "normalized_username": fetch_user.username,
        "access_token": access_token,
    }), 200


def create_user(user_name: str):
    username = _normalize_username(user_name)

    if not username:
        return jsonify({"error": "username is required"}), 400

    fetch_user = Users.query.filter_by(username=username).first()
    if fetch_user:
        return jsonify({"error": "username already exists"}), 409

    current_datetime = datetime.datetime.utcnow()
    user_id = _generate_user_id(username)
    add_user = Users(user_id=user_id, username=username, created_timestamp=current_datetime)

    db.session.add(add_user)
    db.session.commit()

    access_token = create_access_token(identity=username)
    return jsonify({
        "user_id": user_id,
        "username": _display_username(user_name, username),
        "normalized_username": username,
        "access_token": access_token,
        "created_timestamp": current_datetime.isoformat(),
    }), 201


def create_tweet(tweet_load: Dict[str, str]):
    username = _normalize_username(tweet_load.get("uname"))
    tweet_body = (tweet_load.get("tweetbody") or "").strip()

    if not username:
        return jsonify({"error": "uname is required"}), 400

    if not (1 < len(tweet_body) < 141):
        return jsonify({"error": "tweetbody must be between 2 and 140 characters"}), 400

    fetch_user = Users.query.filter_by(username=username).first()
    if not fetch_user:
        return jsonify({"error": "user not found"}), 404

    current_datetime = datetime.datetime.utcnow()
    tweet_id = uuid.uuid4().hex

    add_tweet = TweetData(
        tweet_id=tweet_id,
        user_id=fetch_user.user_id,
        tweet_text=tweet_body,
        created_timestamp=current_datetime,
    )

    db.session.add(add_tweet)
    db.session.commit()

    return jsonify({
        "tweet_id": tweet_id,
        "created_timestamp": current_datetime.isoformat(),
    }), 201


def get_tweets_not_older(histdata: Dict[str, str]):
    username = _normalize_username(histdata.get("uname"))
    if not username:
        return jsonify({"error": "uname is required"}), 400

    date_str = histdata.get("grtndate")
    if not date_str:
        return jsonify({"error": "grtndate is required"}), 400

    try:
        entered_date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        return jsonify({"error": "grtndate must be in DD/MM/YYYY format"}), 400

    fetch_user = Users.query.filter_by(username=username).first()
    if not fetch_user:
        return jsonify({"error": "user not found"}), 404

    start_datetime = datetime.datetime.combine(entered_date, datetime.time.min)

    tweets: Iterable[TweetData] = (
        TweetData.query.filter(
            TweetData.user_id == fetch_user.user_id,
            TweetData.created_timestamp >= start_datetime,
        )
        .order_by(TweetData.created_timestamp.asc())
        .all()
    )

    if not tweets:
        return jsonify({"error": "tweets not found"}), 404

    response_payload: List[Dict[str, str]] = [
        {
            "tweet_id": tweet.tweet_id,
            "tweet_text": tweet.tweet_text,
            "created_timestamp": tweet.created_timestamp.isoformat(),
        }
        for tweet in tweets
    ]

    return jsonify({
        "num_of_tweets": len(response_payload),
        "tweets": response_payload,
    }), 200


def delete_tweets_by_user(user_name: str):
    username = _normalize_username(user_name)
    if not username:
        return jsonify({"error": "username is required"}), 400

    fetch_user = Users.query.filter_by(username=username).first()
    if not fetch_user:
        return jsonify({"error": "user not found"}), 404

    tweets_to_delete = list(
        db.session.execute(
            select(TweetData.tweet_id, TweetData.tweet_text).where(TweetData.user_id == fetch_user.user_id)
        )
    )

    if not tweets_to_delete:
        return jsonify({"error": "tweets not found"}), 404

    db.session.execute(delete(TweetData).where(TweetData.user_id == fetch_user.user_id))
    db.session.commit()

    payload = [
        {"tweet_id": row.tweet_id, "tweet_text": row.tweet_text}
        for row in tweets_to_delete
    ]

    return jsonify({
        "num_of_tweets": len(payload),
        "tweets": payload,
    }), 200
