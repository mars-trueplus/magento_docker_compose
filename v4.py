import xlrd
import subprocess

php_versions_file = 'magento_version.xlsx'

wb = xlrd.open_workbook(php_versions_file)
sheet = wb.sheet_by_index(0)

n = sheet.nrows

# for i in range(1, 2):
for i in range(int((3*n)/6), int((4*n)/6)):
    PHP_VERSION = sheet.cell_value(i, 0)
    docker_filename = "m2_apache2-php%s" % PHP_VERSION
    dockerfile = "build-folder-m2/{0}/{0}".format(docker_filename)
    build_context_folder = "build-folder-m2/%s" % (docker_filename)
    build_command = "docker build -f %s -t marstrueplus/magento2.2.x:apache2-php%s %s" % (dockerfile, PHP_VERSION, build_context_folder)
    start_str = "*" * 100 + "\n" + "*" * 100 + "\nStart building %s image \n" % docker_filename + "*" * 100 + "\n" + "*" * 100 + "\n"
    subprocess.run(["echo", start_str])
    subprocess.run(build_command, shell=True)
