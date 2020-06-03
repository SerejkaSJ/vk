import re
import os
import requests
import random
from download_image import download_image
from dotenv import load_dotenv


V_API = '5.19'


def load_comics():
    response = requests.get("https://xkcd.com/info.0.json")
    response_json = response.json()
    number_comics = response_json['num']
    id_comics = random.randint(0,int(number_comics))
    response = requests.get("https://xkcd.com/{}/info.0.json".format(id_comics))
    link_load_comics = response_json['img']
    name_comics = response_json['safe_title']
    comment = response_json['alt']
    download_image(link_load_comics, '{}.png'.format(name_comics))
    return comment, name_comics
        
    
def upload_to_server(name_comics, client_id, access_token):
    print('client_id',client_id)
    payload = {
        'access_token' : access_token,
        'group_id' : client_id,
        'v' : V_API,
    }
    response = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params = payload)
    response_json = response.json()
    print(response.url)
    print(response.text)
    upload_url = response_json['response']['upload_url']
    with open("{}.png".format(name_comics), 'rb') as image_file_descriptor:
        data = {
            'photo' : image_file_descriptor
           }
        response = requests.post(upload_url, files = data)
        photo_json = response_json['photo']
        photo_hash = response_json['hash']
        server = response_json['server']
        return photo_json, photo_hash, server
    
    
def save_photo(photo_json, photo_hash, server, client_id, access_token):
    data = {
        'access_token' : access_token,
        'group_id' : client_id,
        'photo' : photo_json, 
        'hash' : photo_hash, 
        'server' : server, 
        'v' : V_API,
    }
    response = requests.post("https://api.vk.com/method/photos.saveWallPhoto", data = data)
    response_json = response.json()
    media_id = response_json['response'][0]['id']
    owner_id = response_json['response'][0]['owner_id']
    return media_id, owner_id
    

def posting_comics(media_id, owner_id, group_id, access_token):
    data = {
        'access_token' : access_token,
        'owner_id' : group_id,
        'from_group' : '1',
        'attachments' : 'photo{}_{}'.format(owner_id, media_id),
        'message' : comment,
        'v' : V_API,
    }

    response = requests.post("https://api.vk.com/method/wall.post", data = data)

if __name__ == "__main__":
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    access_token = os.getenv("ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")
    comment, name_comics = load_comics()
    try:
        photo_json, photo_hash, server = upload_to_server(name_comics, client_id, access_token)
        media_id, owner_id = save_photo(photo_json, photo_hash, server, client_id, access_token)
        posting_comics(media_id, owner_id, group_id, access_token)
    except requests.exceptions.HTTPError as error:
        print('Error: ', error)
    finally:
        os.remove("{}.png".format(name_comics))
