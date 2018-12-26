import xlrd


def generate_magento_docker_file():
    local_con = Connection('localhost')
    php_versions = get_php_versions()
    demo_file = open('all_m2/demo', 'r+')
    demo_content = demo_file.readlines()
    for php_version in php_versions:
        new_content = demo_content.copy()
        apache_php_version = "apache2-php%s" % PHP_VERSION
        line1 = "FROM marstrueplus/%s\n" % apache_php_version
        line4 = 'LABEL description="Apache 2 - PHP %s"\n' % PHP_VERSION

        new_content[1 - 1] = line1
        new_content[4 - 1] = line4

        with open('all_m2/m2_%s' % apache_php_version, 'w') as f:
            f.writelines(new_content)


file = 'magento_version.xlsx'

wb = xlrd.open_workbook(file)
sheet = wb.sheet_by_index(0)

demo_file = open('all_m2/demo', "r+")
demo_content = demo_file.readlines()
for i in range(1, sheet.nrows):
    new_content = demo_content.copy()
    PHP_VERSION = sheet.cell_value(i, 0)
    apache_php_version = "apache2-php%s" % PHP_VERSION
    line1 = "FROM marstrueplus/%s\n" % apache_php_version
    line4 = 'LABEL description="Apache 2 - PHP %s"\n' % PHP_VERSION

    new_content[1 - 1] = line1
    new_content[4 - 1] = line4

    f = open("all_m2/m2_%s" % apache_php_version, "w+")
    f.writelines(new_content)
    f.close()
