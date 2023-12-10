import hashlib
import binascii
import os
import datetime


def password(password):
    """Hash a password for storing"""
    #salt = hashlib.sha1(os.urandom(60)).hexdigest().encode('ascii')
    salt = b'de0950b95e30594b52e28e3fc61dd4ca6c2f250a';
    pwdhash = hashlib.pbkdf2_hmac('sha1', password.encode('utf-8'), salt, 1000000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash.decode('ascii')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def register(conn):
    conn.create_function('password', 1, password)
    conn.create_function('now', 0, now)