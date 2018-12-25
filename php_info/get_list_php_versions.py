# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from operator import itemgetter
import re
import requests


def value_contain_string(val, c_str):
    return c_str in val


def get_stable_version():
    res = []
    url = 'http://php.net/downloads.php'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    h3_tag_version = soup.find_all('h3', class_='title')
    php_versions = []

    for tag in h3_tag_version:
        php_versions.append(re.sub('[^0-9.]', '', tag['id']))

    php_versions = [v for v in php_versions if int(v.split('.')[0]) >= 7]

    for php_version in php_versions:
        sha256 = soup.find('a', string='php-%s.tar.xz' % php_version).find_next_sibling('span', class_='sha256').text
        res.append({
            'php_version': php_version,
            'sha256': sha256
        })

    return res


def get_unsupported_version():
    res = []
    url = 'http://php.net/releases/'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')

    php_versions = []
    h2_tags = soup.find_all('h2')
    for tag in h2_tags:
        # get only php version >= 7.0.0
        if int(tag.text.split('.')[0]) >= 7:
            php_versions.append(tag.text)
    for php_version in php_versions:
        sha256 = soup.find(href=re.compile('%s.tar.xz' % php_version)).find_next_sibling('span', class_='sha256sum').text.split(' ')[-1]
        res.append({
            'php_version': php_version,
            'sha256': sha256
        })

    return res


if __name__ == '__main__':
    res = get_stable_version() + get_unsupported_version()
    res = sorted(res, key=itemgetter('php_version'), reverse=True)

    # existed_lines = ''
    with open('php_versions.csv', 'r') as f:
        existed_lines = f.read()

    with open('php_versions.csv', 'a+') as f:
        for php_info in res:
            line = '%s %s' % (php_info['php_version'], php_info['sha256'])
            if line not in existed_lines:
                f.write(line + '\n')