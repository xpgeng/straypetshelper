# -*- coding: utf-8 -*-

import sae.kvdb
import time
from time import strftime, localtime
from sae.storage import Connection, Bucket


def pets_number():
    """
        count the number of  the pets
    """
    kv = sae.kvdb.Client()
    if kv.get('petsnumber'):
        number = kv.get('petsnumber') + 1
        kv.replace('petsnumber', number)
        return number
    else:
        kv.set('petsnumber', 1)
        return 1
    kv.disconnect_all()


def add_to_dogset(dogkey):
    kv = sae.kvdb.Client()
    if kv.get('dogset'):
        dogs = kv.get('dogset')
        dogs.append(str(dogkey))
        kv.set ('dogset',dogs)
    else:
        dogs = []
        dogs.append(str(dogkey))
        kv.set('dogset', dogs)
    kv.disconnect_all()

def add_to_catset(catkey):
    kv = sae.kvdb.Client()
    if kv.get('catset'):
        cats = kv.get('catset')
        cats.append(str(catkey))
        kv.set ('catset',cats)
    else:
        cats = []
        cats.append(str(catkey))
        kv.set('catset', cats)
    kv.disconnect_all()

def add_to_elsepetset(elsepetkey):
    kv = sae.kvdb.Client()
    if kv.get('elsepetset'):
        elsepets = kv.get('elsepetset')
        elsepets.append(str(elsepetkey))
        kv.set ('elsepetset',elsepets)
    else:
        elsepets = []
        elsepets.append(str(elsepetkey))
        kv.set('elsepetset', elsepets)
    kv.disconnect_all()

def save_data(pet_title,species,location,tel, supplement, photo_url, user_id):
    """
    """
    item_number = pets_number()
    kv = sae.kvdb.Client()
    if species == '狗狗':
        key = str('s:d'+strftime("%y%m%d%H%M%S" , localtime()))
    elif species == '猫猫':
        key = str('s:c'+strftime("%y%m%d%H%M%S" , localtime()))
    else:
        key = str('s:e'+strftime("%y%m%d%H%M%S" , localtime()))
    print key
    now = time.time()
    date = strftime("%Y/%m/%d" , localtime(now))
    value = {'pet_title':pet_title, 'species': species,'location':location, 'username':user_id,
        'tel':tel, 'supplement':supplement, 'photo_url':photo_url,'time':now, 'date':date}
    kv.set(key, value)
    kv.disconnect_all()
    return key


def _save_data(pet_title,species,location,tel,supplement, photo_url, user_id):
    """
        key is like this form: 151204112340 which is convenient
        to search according to datetime.
    """
    item_number = pets_number()
    kv = sae.kvdb.Client()
    now = time.time()
    date = strftime("%Y/%m/%d", localtime(now))
    key = str(user_id+strftime("%y%m%d%H%M%S" , localtime()))
    value = {'pet_title':pet_title, 'species': species,'location':location, 
            'tel':tel, 'supplement':supplement, 'photo_url':photo_url,
            'time':now, 'date':date}
    kv.set(key, value)
    if species == '狗狗':
        add_to_dogset(key)
    elif species == '猫猫':
        add_to_catset(key)
    else:
        add_to_elsepetset(key)
    kv.disconnect_all()
    return key

def del_pet(pet_id):
    kv = sae.kvdb.Client()
    image_url = kv.get(pet_id)['photo_url']
    object_name = image_url.split('/')[-1]
    kv.delete(pet_id)
    number = kv.get('petsnumber') - 1
    kv.replace('petsnumber', number)
    c = Connection()
    bucket = c.get_bucket('images')
    bucket.delete_object(object_name)
    kv.disconnect_all()
