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
    docker_filename = "apache2-php%s" % PHP_VERSION

    dic_src = "build-folder/demo"
    dic_dest = "build-folder/%s" % docker_filename
    copy_folder(dic_src, dic_dest)

    file_src = "all/%s" % docker_filename
    file_dest = "build-folder/{0}/{0}".format(docker_filename)
    copy_file(file_src, file_dest)
