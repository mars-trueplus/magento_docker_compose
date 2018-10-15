import xlrd
import shutil
import errno


def copy_folder(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Can\'t copy directory, something went wrong ', e)


def copy_file(src, dest):
    try:
        shutil.copyfile(src, dest)
    except OSError as e:
        print(e)


php_versions_file = 'magento_version.xlsx'

wb = xlrd.open_workbook(php_versions_file)
sheet = wb.sheet_by_index(0)

for i in range(1, sheet.nrows):
    PHP_VERSION = sheet.cell_value(i, 0)
    docker_filename = "m2_apache2-php%s" % PHP_VERSION
    compose_folder_name = "Apache2-Mysql5.7-PHP%s" % PHP_VERSION

    dic_src = "docker-compose-folder/demo"
    dic_dest = "docker-compose-folder/%s" % compose_folder_name
    copy_folder(dic_src, dic_dest)

    file_src = "all_docker_compose_file/%s" % docker_filename
    file_dest = "docker-compose-folder/{}/{}".format(compose_folder_name, 'docker-compose.yml')
    copy_file(file_src, file_dest)
