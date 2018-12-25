# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from operator import itemgetter
import re
import requests


def value_contain_string(val, c_str):
    return c_str in val


def is_int(val):
    try:
        int(val)
        return True
    except ValueError as e:
        return False


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
        php_version = tag.text
        part_versions = [int(x) for x in php_version.split('.') if is_int(x)]
        if part_versions[1] >=1 :
            a = 1
        if len(part_versions) < 3 or \
                part_versions[0] < 7 or \
                (part_versions[0] == 7 and part_versions[1] == 0 and part_versions[2] < 13):
            continue
        php_versions.append(php_version)
    for php_version in php_versions:
        sha256 = soup.find(href=re.compile('%s.tar.xz' % php_version)).find_next_sibling('span', class_='sha256sum').text.split(' ')[-1]
        res.append({
            'php_version': php_version,
            'sha256': sha256
        })

    return res


def get_all_php_versions():
    # get only php version >= 7.0.13 (magento 2.2.x - 2.3.x)
    res = []
    stable_versions = get_stable_version()
    unsupported_versions = get_unsupported_version()
    all = stable_versions + unsupported_versions
    for info in all:
        res.append(info)
    return sorted(res, key=itemgetter('php_version'), reverse=True)


if __name__ == '__main__':
    res = get_all_php_versions()
    with open('php_versions.csv', 'r') as f:
        existed_lines = f.read()

    with open('php_versions.csv', 'a+') as f:
        for php_info in res:
            line = '%s %s' % (php_info['php_version'], php_info['sha256'])
            if line not in existed_lines:
                f.write(line + '\n')
