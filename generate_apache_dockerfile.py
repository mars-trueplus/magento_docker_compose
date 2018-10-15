import xlrd

file = 'magento_version.xlsx'

wb = xlrd.open_workbook(file)
#!/usr/bin/env python
sheet = wb.sheet_by_index(0)
file_name = "apache2-php%s"

# generate dockerfiles: all docker php version
demo_file = open('all/demo', "r+")
demo_content = demo_file.readlines()

for i in range(1, sheet.nrows):
	new_content = demo_content.copy()
	PHP_VERSION = sheet.cell_value(i, 0)	
	PHP_SHA256 = sheet.cell_value(i, 1)
	gpg1 = sheet.cell_value(i, 2)
	gpg2 = sheet.cell_value(i, 3)
	gpg3 = sheet.cell_value(i, 4)

	GPG_KEYS = "%s %s %s" % (gpg1, gpg2, gpg3)
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

	new_content[44-1] = line44
	new_content[46-1] = line46
	new_content[47-1] = line47
	new_content[48-1] = line48
	new_content[49-1] = line49
	new_content[64-1] = line64
	new_content[65-1] = line65
	new_content[66-1] = line66
	new_content[68-1] = line68
	new_content[72-1] = line72

	f = open("all/apache2-php%s" % PHP_VERSION, "w+")
	f.writelines(new_content)
	f.close()