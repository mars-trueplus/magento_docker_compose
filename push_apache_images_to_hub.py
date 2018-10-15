import xlrd
import subprocess

php_versions_file = 'magento_version.xlsx'

wb = xlrd.open_workbook(php_versions_file)
sheet = wb.sheet_by_index(0)

for i in range(1, sheet.nrows):
    PHP_VERSION = sheet.cell_value(i, 0)
    docker_filename = "apache2-php%s" % PHP_VERSION

    push_command = "docker push marstrueplus/%s" % docker_filename
    start_str = "*" * 50 + "\n" + "*" * 50 + "\nStart pushing %s image \n" % docker_filename + "*" * 50 + "\n" + "*" * 50 + "\n"
    subprocess.call(["echo", start_str])
    subprocess.call(push_command, shell=True)
