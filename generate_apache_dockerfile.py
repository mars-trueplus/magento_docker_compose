# -*- coding: utf-8 -*-

import os
import re
from fabric import Connection
import subprocess


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
    php_version_f = 'php_info/php_versions.csv'
    with open(php_version_f, 'r') as f:
        php_versions = f.readlines()

    return php_versions


def generate_apache_php_build_files():
    # generate dockerfiles: all docker php version
    demo_file = open('all/demo', "r+")
    demo_content = demo_file.readlines()
    php_versions = get_php_versions()

    for line in php_versions:
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

    for line in php_versions:
        PHP_VERSION = line.split(' ')[0]
        docker_filename = 'apache2-php%s' % PHP_VERSION
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

    all_apache_files = os.path.abspath('all')
    # local_con.local('rm -rf %s/apache*' % all_apache_files)


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


def build_apache_php_images():
    php_versions = get_php_versions()
    for line in php_versions:
        php_version = line.split(' ')[0]
        docker_filename = "apache2-php%s" % php_version
        dockerfile = "build_folder/{0}/{0}".format(docker_filename)
        dockerfile_path = os.path.abspath(dockerfile)
        build_context = "build_folder/%s" % (docker_filename)
        build_context_path = os.path.abspath(build_context)
        build_command = "docker build -f %s -t marstrueplus/%s %s" % (dockerfile_path, docker_filename, build_context_path)
        start_str = "*" * 50 + "\n" + "*" * 50 + "\nStart building %s image \n" % docker_filename + "*" * 50 + "\n" + "*" * 50 + "\n"
        subprocess.call(["echo", start_str])
        subprocess.call(build_command, shell=True)


if __name__ == '__main__':
    # run separate below functions
    # generate_apache_php_build_files()
    # generate_apache_php_build_folder()
    build_apache_php_images()
    # generate_magento_build_files()
    pass
