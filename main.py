import os
import random
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

VK_METHODS_URL = 'https://api.vk.com/method/'
COMIX_DIR = 'images'
COMIX_FROM = 1
COMIX_TO = 2600


def upload_file_to_server(upload_url, pathfile, comment=None):
    with open(pathfile, 'rb') as file:
        response = requests.post(upload_url, files={'photo': file})
        response.raise_for_status()
        server_answer = response.json()

    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'group_id': os.getenv('VK_GROUP_ID'),
        'server': server_answer['server'],
        'photo': server_answer['photo'],
        'hash': server_answer['hash'],
        'v': os.getenv('VK_API_VER')
    }
    url = VK_METHODS_URL + 'photos.saveWallPhoto'
    response = requests.get(url, params=params)
    response.raise_for_status()
    url = VK_METHODS_URL + 'wall.post'
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'attachments': f'photo{response.json()["response"][0]["owner_id"]}_{response.json()["response"][0]["id"]}',
        'owner_id': -int(os.getenv('VK_GROUP_ID')),
        'from_group': 1,
        'message': comment,
        'v': os.getenv('VK_API_VER')
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_uploadserver_url():
    url = VK_METHODS_URL + 'photos.getWallUploadServer'
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'group_id': os.getenv('VK_GROUP_ID'),
        'v': os.getenv('VK_API_VER')
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_vk_groups():
    url = 'https://api.vk.com/method/groups.get'
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'extended': 1,
        'v': os.getenv('VK_API_VER')
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def comix_is_exist(comix_num):
    url = f'https://xkcd.com/{comix_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    filename = os.path.basename(urlparse(response.json()['img']).path)
    filepath = os.path.join(COMIX_DIR, filename)
    return True if os.path.exists(filepath) else False


def get_comix():
    comix_num = 1
    while comix_is_exist(comix_num):
        comix_num = random.randint(COMIX_FROM, COMIX_TO)
    url = f'https://xkcd.com/{comix_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comix_content = response.json()
    return {
        'img_path': download_comix_img(comix_content['img']),
        'comment': comix_content['alt']
    }


def download_comix_img(img_url):
    os.makedirs(COMIX_DIR, exist_ok=True)
    img_path = os.path.join(COMIX_DIR, os.path.basename(urlparse(img_url).path))
    response = requests.get(img_url)
    response.raise_for_status()
    with open(img_path, 'wb') as file:
        file.write(response.content)
    return img_path


if __name__ == '__main__':
    load_dotenv()
    comix = get_comix()
    upload_file_to_server(get_uploadserver_url(), comix['img_path'], comix['comment'])
