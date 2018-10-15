import xlrd

file = 'magento_version.xlsx'

wb = xlrd.open_workbook(file)
sheet = wb.sheet_by_index(0)

demo_file = open('all_docker_compose_file/demo', "r+")
demo_content = demo_file.readlines()
for i in range(1, sheet.nrows):
    new_content = demo_content.copy()
    PHP_VERSION = sheet.cell_value(i, 0)
    apache_php_version = "apache2-php%s" % PHP_VERSION
    line4 = '    image: marstrueplus/magento2.2.x:%s\n' % apache_php_version
    new_content[4 - 1] = line4

    f = open("all_docker_compose_file/m2_%s" % apache_php_version, "w")
    f.writelines(new_content)
    f.close()
