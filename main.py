import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

VK_METHODS_URL = 'https://api.vk.com/method/'


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


def get_comix():
    url = 'https://xkcd.com/630/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comix_content = response.json()
    return {
        'img_path': download_comix_img(comix_content['img']),
        'comment': comix_content['alt']
    }


def download_comix_img(img_url):
    path = 'images/' + os.path.basename(urlparse(img_url).path)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


if __name__ == '__main__':
    load_dotenv()
    comix = get_comix()
    upload_file_to_server(get_uploadserver_url(), comix['img_path'], comix['comment'])
