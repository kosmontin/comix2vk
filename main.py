import os
import random
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

VK_METHODS_URL = 'https://api.vk.com/method/'
COMICS_FROM = 1
COMICS_TO = 2600


def upload_file_to_server(upload_url, filename, comment=None):
    with open(filename, 'rb') as file:
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
    server_answer = response.json()
    if 'error' in server_answer.keys():
        return server_answer
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'attachments': f'photo{server_answer["response"][0]["owner_id"]}_{server_answer["response"][0]["id"]}',
        'owner_id': -int(os.getenv('VK_GROUP_ID')),
        'from_group': 1,
        'message': comment,
        'v': os.getenv('VK_API_VER')
    }
    url = VK_METHODS_URL + 'wall.post'
    response = requests.get(url, params=params)
    response.raise_for_status()
    server_answer = response.json()
    if 'response' in server_answer.keys():
        with open('posted_comics.txt', 'a') as posted_file:
            posted_file.write(f'{filename}\n')
    return server_answer


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


def comic_is_posted(comic_num):
    url = f'https://xkcd.com/{comic_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    filename = os.path.basename(urlparse(response.json()['img']).path)
    if os.path.exists('posted_comics.txt'):
        with open('posted_comics.txt', 'r') as file:
            posted_comics = file.readlines()
        if filename in posted_comics:
            return True
    else:
        return False


def get_comic():
    while True:
        comic_num = random.randint(COMICS_FROM, COMICS_TO)
        if not comic_is_posted(comic_num):
            break
    url = f'https://xkcd.com/{comic_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_content = response.json()
    return {
        'filename': download_comix_img(comic_content['img']),
        'comment': comic_content['alt']
    }


def download_comix_img(img_url):
    filename = os.path.basename(urlparse(img_url).path)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def post_comic():
    load_dotenv()
    comic = get_comic()
    post_result = upload_file_to_server(get_uploadserver_url(), comic['filename'], comic['comment'])
    if 'response' in post_result.keys():
        print('Комикс опубликован')
        os.remove(comic['filename'])
    elif 'error' in post_result.keys():
        print('Ошибка публикации:\n', post_result['error']['error_msg'])


if __name__ == '__main__':
    post_comic()
