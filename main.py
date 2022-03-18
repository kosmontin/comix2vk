import os
import random
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

VK_METHODS_URL = 'https://api.vk.com/method/'


def upload_file_to_server(upload_url, filename):
    with open(filename, 'rb') as file:
        response = requests.post(upload_url, files={'photo': file})
        response.raise_for_status()
    return response.json()


def save_file_to_server(server_answer):
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'group_id': os.getenv('VK_GROUP_ID'),
        'server': server_answer['server'],
        'photo': server_answer['photo'],
        'hash': server_answer['hash'],
        'v': os.getenv('VK_API_VER')
    }
    url = f'{VK_METHODS_URL}photos.saveWallPhoto'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def post_to_wall(server_answer, comment=None):
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'attachments': f'photo{server_answer["response"][0]["owner_id"]}_{server_answer["response"][0]["id"]}',
        'owner_id': -int(os.getenv('VK_GROUP_ID')),
        'from_group': 1,
        'message': comment,
        'v': os.getenv('VK_API_VER')
    }
    url = f'{VK_METHODS_URL}wall.post'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_uploadserver_url():
    url = f'{VK_METHODS_URL}photos.getWallUploadServer'
    params = {
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'group_id': os.getenv('VK_GROUP_ID'),
        'v': os.getenv('VK_API_VER')
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_posted_comics():
    if os.path.exists('posted_comics.txt'):
        with open('posted_comics.txt', 'r') as file:
            posted_comics = file.readlines()
        return posted_comics
    return None


def get_comic(comics_count):
    posted_comics = get_posted_comics()
    for _ in range(1, comics_count+1):
        comic_num = random.randint(1, comics_count)
        if comic_num not in posted_comics:
            break
    else:
        raise ValueError('All comics was posted. Please, delete "posted_comics.txt" file')
    url = f'https://xkcd.com/{comic_num}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_content = response.json()
    return {
        'img_url': download_comix_img(comic_content['img']),
        'comment': comic_content['alt'],
        'comic_num': comic_num
    }


def download_comix_img(img_url):
    filename = os.path.basename(urlparse(img_url).path)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def get_comics_count():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def post_comic():
    load_dotenv()
    comic = get_comic(get_comics_count())
    upload_url = get_uploadserver_url()
    answer = upload_file_to_server(upload_url, comic['img_url'])
    answer = save_file_to_server(answer)
    answer = post_to_wall(answer, comic['comment'])
    if 'response' in answer.keys():
        print('Комикс опубликован')
        os.remove(comic['img_url'])
    elif 'error' in answer.keys():
        print('Ошибка публикации:\n', answer['error']['error_msg'])


if __name__ == '__main__':
    post_comic()
