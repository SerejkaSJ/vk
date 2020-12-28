import re
import os
import requests
import random
from download_image import download_image
from dotenv import load_dotenv


API_VERSION = '5.19'


class APIError(BaseException):
    """Error API VK"""


def load_comics():
    response = requests.get("https://xkcd.com/info.0.json")
	response.raise_for_status()
    comicses_info = response.json()
    count_comics = comicses_info['num']
    id_comics = random.randint(0,int(count_comics))
    response = requests.get("https://xkcd.com/{}/info.0.json".format(id_comics))
	response.raise_for_status()
    comics_info = response.json()
    link_load_comics = comics_info['img']
    name_comics = comics_info['safe_title']
    comment = comics_info['alt']
    download_image(link_load_comics, '{}.png'.format(name_comics))
    return comment, name_comics
        
    
def upload_to_server(name_comics, client_id, access_token):
    payload = {
        'access_token' : access_token,
        'group_id' : client_id,
        'v' : API_VERSION,
    }
    response = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params = payload)
	response.raise_for_status()
    upload_info = response.json()
    if 'error' in upload_info:
        raise APIError('Error upload to server')
    upload_url = upload_info['response']['upload_url']
    with open("{}.png".format(name_comics), 'rb') as image_file_descriptor:
        data = {
            'photo' : image_file_descriptor
           }
        response = requests.post(upload_url, files = data)
		response.raise_for_status()
        photo = upload_info['photo']
        photo_hash = upload_info['hash']
        server = upload_info['server']
        return photo, photo_hash, server
    
    
def save_photo(photo_json, photo_hash, server, client_id, access_token):
    data = {
        'access_token' : access_token,
        'group_id' : client_id,
        'photo' : photo_json, 
        'hash' : photo_hash, 
        'server' : server, 
        'v' : API_VERSION,
    }
    response = requests.post("https://api.vk.com/method/photos.saveWallPhoto", data = data)
	response.raise_for_status()
    save_photo_info = response.json()
    if 'error' in save_photo_info:
        raise APIError('Error save photo')
	save_photo_info_curr = save_photo_info['response'][0]
    media_id = save_photo_info_curr['id']
    owner_id = save_photo_info_curr['owner_id']
    return media_id, owner_id
    

def posting_comics(media_id, owner_id, group_id, access_token):
    data = {
        'access_token' : access_token,
        'owner_id' : group_id,
        'from_group' : '1',
        'attachments' : 'photo{}_{}'.format(owner_id, media_id),
        'message' : comment,
        'v' : API_VERSION,
    }

    response = requests.post("https://api.vk.com/method/wall.post", data = data)
	response.raise_for_status()
    posting_info = response.json() 
    if 'error' in posting_info:
        raise APIError('Error posting comics')

if __name__ == "__main__":
    load_dotenv()
    client_id = os.getenv("CLIENT_ID_VK")
    access_token = os.getenv("ACCESS_TOKEN_VK")
    group_id = os.getenv("GROUP_ID_VK")
    comment, name_comics = load_comics()
    try:
        photo_json, photo_hash, server = upload_to_server(name_comics, client_id, access_token)
        media_id, owner_id = save_photo(photo_json, photo_hash, server, client_id, access_token)
        posting_comics(media_id, owner_id, group_id, access_token)
    except requests.exceptions.HTTPError as error:
        print('Error: ', error)
    except APIError as error:
        print('Error: ', error)
    finally:
        os.remove("{}.png".format(name_comics))
