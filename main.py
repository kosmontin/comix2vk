import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from pprint import pprint


def upload_file_to_server(pathfile, upload_url):
    url = upload_url
    with open(pathfile, 'rb') as file:
        files = {'photo': file}
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


def get_uploadserver_info():
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
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
    url = 'https://xkcd.com/619/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comix_content = response.json()
    print(comix_content['alt'])
    download_comix_img(comix_content['img'])


def download_comix_img(img_url):
    response = requests.get(img_url)
    response.raise_for_status()
    with open(os.path.basename(urlparse(img_url).path), 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    load_dotenv()
    pprint(upload_file_to_server('./supported_features.png', get_uploadserver_info()), sort_dicts=False)
