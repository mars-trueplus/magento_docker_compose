import xlrd
import subprocess

php_versions_file = 'magento_version.xlsx'

wb = xlrd.open_workbook(php_versions_file)
sheet = wb.sheet_by_index(0)

# for i in range(1, 2):
for i in range(1, sheet.nrows):
    PHP_VERSION = sheet.cell_value(i, 0)
    docker_filename = "apache2-php%s" % PHP_VERSION
    dockerfile = "build-folder/{0}/{0}".format(docker_filename)
    build_context_folder = "build-folder/%s" % (docker_filename)
    build_command = "sudo docker build -f %s -t marstrueplus/%s %s" % (dockerfile, docker_filename, build_context_folder)
    start_str = "*" * 50 + "\n" + "*" * 50 + "\nStart building %s image \n" % docker_filename + "*" * 50 + "\n" + "*" * 50 + "\n"
    subprocess.call(["echo", start_str])
    subprocess.call(build_command, shell=True)
