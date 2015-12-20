# -*- coding: utf-8 -*-

import sae.kvdb
import time
import json
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

def save_data(pet_title, age, gender, sterilization, immunization, \
        health, species,location,tel,supplement, photo_urls, user_id):
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
    value = {'pet_title':pet_title, 'species': species, 'age': age, 'gender': gender,\
    'sterilization': sterilization, 'immunization':immunization, 'health':health, \
    'location':location, 'email':user_id,'tel':tel, 'supplement':supplement,\
    'photo_urls':photo_urls,'time':now, 'date':date}
    kv.set(key, value)
    kv.disconnect_all()
    return key

def change_sequence(petlist):
    import copy
    petlist = copy.deepcopy(petlist)
    petlist = sorted(petlist, key=lambda x:x[1]['time'], reverse=True)
    return petlist



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
    from qiniu import BucketManager
    from qiniu import Auth, put_data

    access_key = "Yqbge2chl_b41gjy90cbK5WUQ8__mwiGuqGzomEG"
    secret_key = "0dV_u7zaIoKkfksdF-4GiCh6UPHXVtr-SegekGll"
    bucket_name = "straypetshelper"
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)

    kv = sae.kvdb.Client()
    image_urls = kv.get(pet_id)['photo_urls']
    for image_url in image_urls:
        key = image_url.split('/')[-1]
        ret, info = bucket.delete(bucket_name, key)
        
    kv.delete(pet_id)
    number = kv.get('petsnumber') - 1
    kv.replace('petsnumber', number)
    kv.disconnect_all()

def add_petkey_to_userId( user_id, petkey):
    kv = sae.kvdb.Client()
    if kv.get(str(user_id)):
        user_dic = kv.get(str(user_id))
        user_dic['pet'].append(str(petkey))
        kv.set(str(user_id),user_dic)
    else:
        use_dic = {}
        user_dic['pet'] = str(petkey)
        kv.set(str(user_id),user_dic)
    kv.disconnect_all()

def get_petdict_according_petspecies(pet_species):
    kv = sae.kvdb.Client()
    if pet_species == 'dog':
        prefix = 's:d'
    elif pet_species == 'cat':
        prefix = 's:c'
    elif pet_species == 'all':
        prefix = 's:'
    else:
        prefix = 's:e'
    keys = [key for key, value in kv.get_by_prefix(prefix)]
    pet_dict = kv.get_multi(keys).items()
    return pet_dict
    kv.disconnect_all()

def get_image_and_petdict(pet_id):
    kv = sae.kvdb.Client()
    pet_id = str(pet_id)
    image = kv.get(pet_id)['photo_urls']
    pet_dict = kv.get(pet_id)
    return image, pet_dict
    kv.disconnect_all()

def search_results(query):
    kv = sae.kvdb.Client()
    data = kv.get_by_prefix('s')
    results = []
    for key, value in data:
        pet_item = [value['pet_title'], value['species'], value['location'],\
            value['supplement'], value['date'], value['email']]
        for item in pet_item:
            if query in str(item):
                results.append(key)
    if results:
        pet_dict = kv.get_multi(results).items()
        pet_dict = change_sequence(pet_dict)
        return pet_dict
    else:
        return None
    kv.disconnect_all()




def check_message(message):
    kv = sae.kvdb.Client()
    print message[0:4]
    if message[0:2] == 'd.':
        key = message[2:]
        content = kv.get(key)
        kv.delete(key)
        return  "%s\n This item has beem deleted." %content
    elif message[0:3] == 'dp.':
        prefix = message[3:]
        keys = kv.getkeys_by_prefix(prefix)
        for key in keys:
            kv.delete(key)
        return "%s\n All the keys' item have been deleted." %keys
    elif message == 'bakckup':
        bucket = Bucket('backup')
        bucket.put()
        data_dict = dict(kv.get_by_prefix(''))
        data_dict = json.dumps(data_dict)
        bucket.put_object('database.json', data_dict)
        return "备份成功!"
    elif message[0:4] == 'get.':
        prefix = message[5:]
        content = dict(kv.get_by_prefix(prefix))
        return '''They are:
               %s
               '''% content
    elif message == 'ca':
        keys = kv.getkeys_by_prefix('')
        for key in keys:
            kv.delete(key)
        return "Database is empty!"
    else:
        return "Sorry, Please check your input..."
    kv.disconnect_all()








































    