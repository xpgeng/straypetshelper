# -*- coding: utf-8 -*-

import sae.kvdb
import time
from time import strftime, localtime
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey
from datetime import timedelta
from werkzeug.security import generate_password_hash, \
        check_password_hash

def users_number():
    """
        count the number of  the pets
    """
    kv = sae.kvdb.Client()
    if kv.get('usersnumber'):
        number = kv.get('usersnumber') + 1
        kv.replace('usersnumber', number)
        return number
    else:
        kv.set('usersnumber', 1)
        return 1
    kv.disconnect_all()



def save_email(email, password, username):
    """
    """
    usersnumber = users_number()
    kv = sae.kvdb.Client()
    now = time.time()
    pwhash = generate_password_hash(password) #hash加密
    message = {'password':pwhash, 'email':email, 'username':username, 'time':now,'pet':[]}
    kv.set(str(email), message)
    kv.disconnect_all()

def add_to_emailset(email):
    kv = sae.kvdb.Client()
    if kv.get('emailset'):
        emails = kv.get('emailset')
        emails.append(str(email))
        kv.set ('emailset',emails)
    else:
        emails = []
        emails.append(str(email))
        kv.set('emailset', emails)
    kv.disconnect_all()

def check_login(email,password):
    """
    """
    kv = sae.kvdb.Client()
    if not email:
        return False
    elif kv.get(str(email)):
        pwhash = kv.get(str(email))['password']
        if check_password_hash(pwhash, password):
            return True
        else:
            return False
    else:
        return False
    kv.disconnect_all()

def check_email(email):
    kv = sae.kvdb.Client()
    if kv.get(str(email)):
        return True       
    else:
        return False        
    kv.disconnect_all()

def get_message_petdict_from_userid(user_id):
    kv = sae.kvdb.Client()
    keys = kv.get(str(user_id))['pet']
    if not keys:
        message = "你还没有发布过小动物信息哦，快去发布吧～"
    else:
        message = "您发布过的小动物："       
    pet_dict = kv.get_multi(keys).items()
    return message, pet_dict
    kv.disconnect_all()
