# -*- coding: utf-8 -*-

import os
import re


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


def update_apache_php_build_file():
    # generate dockerfiles: all docker php version
    php_version_f = 'php_info/php_versions.csv'
    demo_file = open('all/demo', "r+")
    demo_content = demo_file.readlines()

    with open(php_version_f, 'r') as f:
        php_versions = f.readlines()

    for line in php_versions:
        new_content = demo_content.copy()
        PHP_VERSION = line.split(' ')[0]
        PHP_SHA256 = line.split(' ')[1]

        GPG_KEYS = ' '.join(get_gpg_keys(PHP_VERSION))
        PHP_FILENAME = "php-%s.tar.xz" % (PHP_VERSION)
        PHP_URL = "https://secure.php.net/get/%s/from/this/mirror" % (PHP_FILENAME)
        PHP_ASC_URL = "https://secure.php.net/get/%s.asc/from/this/mirror" % (PHP_FILENAME)

        line44 = 'ENV GPG_KEYS %s\n' % (GPG_KEYS)
        line46 = 'ENV PHP_VERSION %s\n' % (PHP_VERSION)
        line47 = 'ENV PHP_FILENAME %s\n' % (PHP_FILENAME)
        line48 = 'ENV PHP_SHA256 %s\n' % (PHP_SHA256)
        line49 = 'ENV PHP_URL="%s" PHP_ASC_URL="%s"\n' % (PHP_URL, PHP_ASC_URL)
        line64 = '	&& wget -O php.tar.xz "%s" \\\n' % (PHP_URL)
        line65 = '	&& echo "%s *php.tar.xz" | sha256sum -c - \\\n' % (PHP_SHA256)
        line66 = '	&& wget -O php.tar.xz.asc "%s" \\\n' % (PHP_ASC_URL)
        line68 = '	&& for key in %s; do \\\n' % (GPG_KEYS)
        line72 = '	&& rm -rf "$GNUPGHOME" "%s.asc"\\\n' % (PHP_FILENAME)

        new_content[44 - 1] = line44
        new_content[46 - 1] = line46
        new_content[47 - 1] = line47
        new_content[48 - 1] = line48
        new_content[49 - 1] = line49
        new_content[64 - 1] = line64
        new_content[65 - 1] = line65
        new_content[66 - 1] = line66
        new_content[68 - 1] = line68
        new_content[72 - 1] = line72

        f = open("all/apache2-php%s" % PHP_VERSION, "w+")
        f.writelines(new_content)
        f.close()


if __name__ == '__main__':
    update_apache_php_build_file()
