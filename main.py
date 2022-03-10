import os
import requests
from urllib.parse import urlparse


def get_img_url():
    url = 'https://xkcd.com/619/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['img']


def download_comix(img_url):
    response = requests.get(img_url)
    response.raise_for_status()
    with open(os.path.basename(urlparse(img_url).path), 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    download_comix(get_img_url())
