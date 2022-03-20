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
    answer = response.json()
    check_response(answer)
    return answer


def save_file_to_server(api_key, group_id, api_ver, server_answer):
    params = {
        'access_token': api_key,
        'group_id': group_id,
        'server': server_answer['server'],
        'photo': server_answer['photo'],
        'hash': server_answer['hash'],
        'v': api_ver
    }
    url = f'{VK_METHODS_URL}photos.saveWallPhoto'
    response = requests.get(url, params=params)
    response.raise_for_status()
    answer = response.json()
    check_response(answer)
    return answer


def post_to_wall(api_key, group_id, api_ver, server_answer, comment=None):
    params = {
        'access_token': api_key,
        'attachments': (f'photo{server_answer["response"][0]["owner_id"]}_'
                        f'{server_answer["response"][0]["id"]}'),
        'owner_id': -int(group_id),
        'from_group': 1,
        'message': comment,
        'v': api_ver
    }
    url = f'{VK_METHODS_URL}wall.post'
    response = requests.get(url, params=params)
    response.raise_for_status()
    answer = response.json()
    check_response(answer)
    return answer


def get_uploadserver_url(api_key, group_id, api_ver):
    url = f'{VK_METHODS_URL}photos.getWallUploadServer'
    params = {
        'access_token': api_key,
        'group_id': group_id,
        'v': api_ver
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    answer = response.json()
    check_response(answer)
    return answer['response']['upload_url']


def get_comic(comic_num):
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


def get_comics_count():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_unique_comics_num(comics_count):
    posted_comics = None
    if os.path.exists('posted_comics.txt'):
        with open('posted_comics.txt', 'r') as file:
            posted_comics = file.readlines()
    for _ in range(1, comics_count + 1):
        comic_num = random.randint(1, comics_count)
        if not posted_comics or comic_num not in posted_comics:
            return comic_num
    else:
        raise ValueError('Все комиксы опубликованы. '
                         'Пожалуйста, удалите файл "posted_comics.txt"')


def write_posted_comic_num(comic_num):
    with open('posted_comics.txt', 'a') as posted_file:
        posted_file.write(f'{comic_num}\n')


def check_response(response):
    if 'error' in response:
        raise SystemError(
            f'Произошла ошибка.\n'
            f'Код ошибки: {response["error"]["error_code"]}\n'
            f'Сообщение: {response["error"]["error_msg"]}\n'
            f'Более подробно по адресу: https://vk.com/dev/errors'
        )


def post_random_comic(api_key, group_id, api_ver, post_only_unique):
    comics_count = get_comics_count()
    if post_only_unique:
        comic_num = get_unique_comics_num(comics_count)
    else:
        comic_num = random.randint(1, comics_count)
    comic = get_comic(comic_num)
    try:
        upload_url = get_uploadserver_url(api_key, group_id, api_ver)
        answer = upload_file_to_server(upload_url, comic['filename'])
        answer = save_file_to_server(api_key, group_id, api_ver, answer)
        post_to_wall(api_key, group_id, api_ver, answer, comic['comment'])
        write_posted_comic_num(comic_num)
    finally:
        os.remove(comic['filename'])


if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    api_ver = os.getenv('VK_API_VER')
    only_unique = os.getenv(
        'POST_UNIQUE_COMIC', False
    ).lower() in ('true', 'yes', '1')
    try:
        post_random_comic(api_key, group_id, api_ver, only_unique)
    except (SystemError, ValueError) as err:
        print(err)
