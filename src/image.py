# -*- coding: utf-8 -*-
import time
from werkzeug import secure_filename
from qiniu import Auth, put_data



def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def process_filename(user_id,filename):
    """
          preprocess filename
    """
    filename_new = "%s%s.%s" % (user_id, int(time.time()), filename)
    return filename_new

def save_image_return_url(filename, file):
    """ 
         return: the url of the image in the storage
    """
    access_key = "Yqbge2chl_b41gjy90cbK5WUQ8__mwiGuqGzomEG"
    secret_key = "0dV_u7zaIoKkfksdF-4GiCh6UPHXVtr-SegekGll"
    bucket_name = "straypetshelper"
    q = Auth(access_key, secret_key)
    key = filename
    token = q.upload_token(bucket_name, key)
    ret, info = put_data(token,key,file.read())

    return "http://7xpby0.com1.z0.glb.clouddn.com/"+filename

def save_image_return_url_sae(filename, file):
    from sae.storage import Connection, Bucket
    c = Connection()
    bucket = c.get_bucket('images')
    bucket.put_object(filename, file.read())
    return bucket.generate_url(filename)


def get_photourls(user_id, pet_photo):
    photo_urls = []
    for pfile in pet_photo:
        if pfile and allowed_file(pfile.filename):
            filename = secure_filename(pfile.filename)
            renew_filename = process_filename(user_id, filename)
            #photo_url = save_image_return_url(renew_filename, pfile)
            photo_url = save_image_return_url_sae(renew_filename, pfile)
            photo_urls.append(photo_url)
        #else:
        	#return    # havn't finished 
    return photo_urls


