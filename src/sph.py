# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sae.kvdb
from time import strftime, localtime
from sae.storage import Connection, Bucket
from sae.ext.storage import monkey
monkey.patch_all()



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_filename(filename):
    """
        This funcion can solve the bug of omitting the Chinese characters in filename.

    """
    if filename in ALLOWED_EXTENSIONS:
        filename_new = "%s.%s" % (int(time.time()), filename)
        return filename_new
    else:
        return filename


def save_image_return_url(filename, file):
    """ 
         return: the url of the image in the storage
    """
    c = Connection()
    bucket = c.get_bucket('imges')
    bucket.put_object(filename, file.read())
    return bucket.generate_url(filename)


def count_items():
    """
        count the number of  the items or pets
    """
    kv = sae.kvdb.Client()
    if kv.get('NumberOfItems'):
        number = kv.get('NumberOfItems') + 1
        kv.replace('NumberOfItems', number)
        return number
    else:
        kv.set('NumberOfItems', 1)
        return 1
    kv.disconnect_all()

def check_location(location, key):
    kv = sae.kvdb.Client()
    if kv.location

def save_data(pet_title,species,location,tel,supplement, photo_url):
    """
        key is like this form: 151204112340 which is convenient
        to search according to datetime.
    """
    item_number = count_items()
    print item_number
    kv = sae.kvdb.Client()
    key = strftime("%y%m%d%H%M%S" , localtime())
    print key
    now = time.time()
    value = {'pet_title':pet_title, 'species': species,'location':location, 
        'tel':tel, 'supplement':supplement, 'photo_url':photo_url,'time':now}
    kv.set(key, value)
    check_location(location)
    kv.disconnect_all()
