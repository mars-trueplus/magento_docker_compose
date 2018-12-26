# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from operator import itemgetter
from fabric import Connection
import os
import re
import requests
import subprocess

BUILD_VERSION = '1'
REPO_OWNER = 'marstrueplus'


def value_contain_string(val, c_str):
    return c_str in val


def is_int(val):
    try:
        int(val)
        return True
    except ValueError as e:
        return False


def get_stable_releases():
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


def get_unsupported_releases():
    res = []
    url = 'http://php.net/releases/'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')

    php_versions = []
    h2_tags = soup.find_all('h2')
    for tag in h2_tags:
        php_version = tag.text
        part_versions = [int(x) for x in php_version.split('.') if is_int(x)]
        if part_versions[1] >= 1:
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


def get_all_php_releases():
    # get only php version >= 7.0.13 (magento 2.2.x - 2.3.x)
    stable_releases = get_stable_releases()
    unsupported_releases = get_unsupported_releases()
    all = stable_releases + unsupported_releases
    res = [info for info in all]
    res = sorted(res, key=itemgetter('php_version'), reverse=True)

    with open('php_info/php_releases.csv', 'r') as f:
        existed_lines = f.read()

    with open('php_info/php_releases.csv', 'a+') as f:
        for php_info in res:
            line = '%s %s' % (php_info['php_version'], php_info['sha256'])
            if line not in existed_lines:
                f.write(line + '\n')

    return True


def get_gpg_keys(php_version):
    res = []
    php_gpg_keys_f = os.path.abspath('php_info/gpg_keys')
    for f in os.listdir(php_gpg_keys_f):
        if f == php_version[0:len(f)]:
            with open(php_gpg_keys_f + '/' + f, 'r') as key_file:
                lines = key_file.readlines()
            for line in lines:
                if line:
                    res.append(re.sub(r'[^a-zA-Z0-9]', '', line))
    return res


def get_php_versions():
    php_version_f = 'php_info/php_releases.csv'
    with open(php_version_f, 'r') as f:
        php_versions = [line.split(' ')[0] for line in f.readlines()]

    return php_versions


def get_php_releases():
    php_releases_file = 'php_info/php_releases.csv'
    with open(php_releases_file, 'r') as f:
        php_releases = f.readlines()

    return php_releases


def generate_apache_php_build_files():
    # generate dockerfiles: all docker php version
    demo_file = open('all/demo', "r+")
    demo_content = demo_file.readlines()
    php_releases = get_php_releases()

    for line in php_releases:
        new_content = demo_content.copy()
        PHP_VERSION = line.split(' ')[0]
        PHP_SHA256 = line.split(' ')[1].replace('\n', '')

        GPG_KEYS = ' '.join(get_gpg_keys(PHP_VERSION))
        PHP_FILENAME = "php-%s.tar.xz" % (PHP_VERSION)
        PHP_URL = "https://secure.php.net/get/%s/from/this/mirror" % (PHP_FILENAME)
        PHP_ASC_URL = "https://secure.php.net/get/%s.asc/from/this/mirror" % (PHP_FILENAME)

        line41 = 'ENV GPG_KEYS %s\n' % (GPG_KEYS)
        line43 = 'ENV PHP_VERSION %s\n' % (PHP_VERSION)
        line44 = 'ENV PHP_FILENAME %s\n' % (PHP_FILENAME)
        line45 = 'ENV PHP_SHA256 %s\n' % (PHP_SHA256)
        line46 = 'ENV PHP_URL="%s" PHP_ASC_URL="%s"\n' % (PHP_URL, PHP_ASC_URL)
        line61 = '	&& wget -O php.tar.xz "%s" \\\n' % (PHP_URL)
        line62 = '	&& echo "%s *php.tar.xz" | sha256sum -c - \\\n' % (PHP_SHA256)
        line63 = '	&& wget -O php.tar.xz.asc "%s" \\\n' % (PHP_ASC_URL)
        line65 = '	&& for key in %s; do \\\n' % (GPG_KEYS)
        line69 = '	&& rm -rf "$GNUPGHOME" "%s.asc"\\\n' % (PHP_FILENAME)

        new_content[41 - 1] = line41
        new_content[43 - 1] = line43
        new_content[44 - 1] = line44
        new_content[45 - 1] = line45
        new_content[46 - 1] = line46
        new_content[61 - 1] = line61
        new_content[62 - 1] = line62
        new_content[63 - 1] = line63
        new_content[65 - 1] = line65
        new_content[69 - 1] = line69

        with open('all/apache2-php%s' % PHP_VERSION, 'w') as f:
            f.writelines(new_content)


def generate_apache_php_build_folder():
    local_con = Connection('localhost')
    php_versions = get_php_versions()

    for php_version in php_versions:
        docker_filename = 'apache2-php%s' % php_version
        dic_src = "build_folder/demo"
        dic_dest = "build_folder/%s" % docker_filename
        dic_src_path = os.path.abspath(dic_src)
        dic_dest_path = os.path.abspath(dic_dest)
        local_con.local('rm -rf {0} && mkdir {0}'.format(dic_dest_path))
        local_con.local('cp -r %s/* %s' % (dic_src_path, dic_dest_path))

        file_src = "all/%s" % docker_filename
        file_dest = "build_folder/{0}/{0}".format(docker_filename)
        file_src_path = os.path.abspath(file_src)
        file_dest_path = os.path.abspath(file_dest)
        local_con.local('cp -r %s %s' % (file_src_path, file_dest_path))


def build_apache_php_images():
    php_versions = get_php_versions()
    for php_version in php_versions:
        docker_filename = "apache2-php%s" % php_version
        dockerfile = "build_folder/{0}/{0}".format(docker_filename)
        dockerfile_path = os.path.abspath(dockerfile)
        build_context = "build_folder/%s" % (docker_filename)
        build_context_path = os.path.abspath(build_context)
        build_command = "docker build -f {dockerfile_path} -t {repo_owner}/{image_name}:{image_version} {build_context_path}".format(
            dockerfile_path=dockerfile_path,
            repo_owner=REPO_OWNER,
            image_name=docker_filename,
            image_version=BUILD_VERSION,
            build_context_path=build_context_path
        )
        start_str = "*" * 50 + "\n" + "*" * 50 + "\nStart building %s image \n" % docker_filename + "*" * 50 + "\n" + "*" * 50 + "\n"
        subprocess.call(["echo", start_str])
        subprocess.call(build_command, shell=True)


def generate_magento_build_files():
    php_versions = get_php_versions()
    demo_file = open('all_m2/demo', 'r+')
    demo_content = demo_file.readlines()
    for php_version in php_versions:
        new_content = demo_content.copy()
        apache_php_version = "apache2-php%s" % php_version
        line1 = "FROM marstrueplus/%s\n" % apache_php_version
        line4 = 'LABEL description="Apache 2 - PHP %s"\n' % php_version

        new_content[1 - 1] = line1
        new_content[4 - 1] = line4

        with open('all_m2/m2_%s' % apache_php_version, 'w') as f:
            f.writelines(new_content)


def generate_magento_build_folder():
    local_con = Connection('localhost')
    php_versions = get_php_versions()
    for php_version in php_versions:
        docker_filename = "m2_apache2-php%s" % php_version

        dic_src = "build_folder_m2/demo"
        dic_dest = "build_folder_m2/%s" % docker_filename
        dic_src_path = os.path.abspath(dic_src)
        dic_dest_path = os.path.abspath(dic_dest)
        local_con.local('rm -rf {0} && mkdir {0}'.format(dic_dest_path))
        local_con.local('cp -r %s/* %s' % (dic_src_path, dic_dest_path))

        file_src = "all_m2/%s" % docker_filename
        file_dest = "build_folder_m2/{0}/{0}".format(docker_filename)
        file_src_path = os.path.abspath(file_src)
        file_dest_path = os.path.abspath(file_dest)
        local_con.local('cp -r %s %s' % (file_src_path, file_dest_path))


def build_magento_images():
    php_versions = get_php_versions()
    for php_version in php_versions:
        docker_filename = "m2_apache2-php%s" % php_version
        dockerfile = "build_folder_m2/{0}/{0}".format(docker_filename)
        dockerfile_path = os.path.abspath(dockerfile)
        build_context = "build_folder_m2/%s" % (docker_filename)
        build_context_path = os.path.abspath(build_context)
        build_command = "sudo docker build -f {dockerfile_path} -t {repo_owner}/{image_name}:v{image_version} {build_context_path}".format(
            dockerfile_path=dockerfile_path,
            repo_owner=REPO_OWNER,
            image_name=docker_filename,
            image_version=BUILD_VERSION,
            build_context_path=build_context_path
        )
        start_str = "*" * 100 + "\n" + "*" * 100 + "\nStart building %s image \n" % docker_filename + "*" * 100 + "\n" + "*" * 100 + "\n"
        subprocess.run(["echo", start_str])
        subprocess.run(build_command, shell=True)


if __name__ == '__main__':
    # run separate below functions
    # get_all_php_releases()
    # generate_apache_php_build_files()
    # generate_apache_php_build_folder()
    # build_apache_php_images()
    # generate_magento_build_files()
    # generate_magento_build_folder()
    build_magento_images()
