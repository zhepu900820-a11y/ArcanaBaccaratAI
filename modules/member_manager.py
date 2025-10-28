# -*- coding: utf-8 -*-
from flask import session

# MVP 內建帳號；之後可改DB或接金流 webhook
USERS = {
    "admin": {"password":"1234", "level":"vip", "expire_at":"2099-12-31"},
    "guest": {"password":"0000", "level":"free", "expire_at":"2099-12-31"}
}

def get_user():
    return session.get("user")

def login_user(username: str):
    info = USERS.get(username, {})
    session["user"] = {"username": username, "level": info.get("level","free"), "expire_at": info.get("expire_at")}

def logout_user():
    session.clear()

def require_login():
    return get_user() is not None
