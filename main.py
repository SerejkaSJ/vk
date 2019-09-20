import re
import os
import requests
import random
from load_image import load_image
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv("client_id")
access_token = os.getenv("access_token")
group_id = os.getenv("group_id")
v_api = '5.19'


def load_comics():
    response = requests.get("https://xkcd.com/info.0.json")
    number_comics = response.json()['num']
    id_comics = random.randint(0,int(number_comics))
    response = requests.get("https://xkcd.com/{}/info.0.json".format(id_comics))
    link_load_comics = response.json()['img']
    name_comics = response.json()['safe_title']
    comment = response.json()['alt']
    load_image(link_load_comics, '{}.png'.format(name_comics))
    return comment, name_comics
    
    
def upload_to_server(name_comics):
    response = requests.get("https://api.vk.com/method/photos.getWallUploadServer?&access_token={}&group_id={}&v={}".format(access_token,client_id,v_api))
    upload_url = response.json()['response']['upload_url']
    image_file_descriptor = open("{}.png".format(name_comics), 'rb')

    data = {
        'photo' : image_file_descriptor
       }
    response = requests.post(upload_url, files = data)
    image_file_descriptor.close()
    photo_json = response.json()['photo']
    hash = response.json()['hash']
    server = response.json()['server']
    return photo_json, hash, server
    
    
def save_photo(photo_json, hash, server):
    data = {
        'access_token' : access_token,
        'group_id' : client_id,
        'photo' : photo_json, 
        'hash' : hash, 
        'server' : server, 
        'v' : v_api,
    }
    response = requests.post("https://api.vk.com/method/photos.saveWallPhoto", data = data)
    media_id = response.json()[u'response'][0]['id']
    owner_id = response.json()['response'][0]['owner_id']
    return media_id, owner_id
    

def post(media_id, owner_id):
    data = {
        'access_token' : access_token,
        'owner_id' : '-' + group_id,
        'from_group' : '1',
        'attachments' : 'photo{}_{}'.format(owner_id, media_id),
        'message' : comment,
        'v' : v_api,
    }

    response = requests.post("https://api.vk.com/method/wall.post", data = data)

if __name__ == "__main__":
    comment, name_comics = load_comics()
    photo_json, hash, server = upload_to_server(name_comics)
    media_id, owner_id = save_photo(photo_json, hash, server)
    post(media_id, owner_id)
    os.remove("{}.png".format(name_comics))
