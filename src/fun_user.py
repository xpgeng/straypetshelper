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



def save_user(username, password, email):
    """
    """
    usersnumber = users_number()
    kv = sae.kvdb.Client()
    now = time.time()
    pwhash = generate_password_hash(password) #hash加密
    message = {'username':username, 'password':pwhash, 'email':email, 'time':now,'pet':[]}
    kv.set(str(username), message)
    kv.disconnect_all()

def add_to_userset(username):
    kv = sae.kvdb.Client()
    if kv.get('userset'):
        users = kv.get('userset')
        users.append(str(username))
        kv.set ('userset',users)
    else:
        users = []
        users.append(str(username))
        kv.set('userset', users)
    kv.disconnect_all()

def check_login(username,password):
    """
    """
    kv = sae.kvdb.Client()
    if not username:
        return False
    elif kv.get(str(username)):
        pwhash = kv.get(str(username))['password']
        if check_password_hash(pwhash, password):
            return True
        else:
            return False
    else:
        return False
    kv.disconnect_all()

def check_user(username):
    kv = sae.kvdb.Client()
    if kv.get(str(username)):
        return True       
    else:
        return False        
    kv.disconnect_all()
