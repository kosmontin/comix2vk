import os
import requests
from urllib.parse import urlparse


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
    get_comix()
