import os, sqlite, types

dbase = 'darbase.sqlite'

headers = {
	'spec': ('name', 'authority', 'summary', 'epoch', 'version', 'release', 'license', 'category', 'url', 'description', 'upstream', 'parent', 'specname'),
	'pkg': ('name', 'version', 'release', 'arch', 'repo', 'dist', 'parent', 'builder', 'filename'),
	'info': ('name', 'summary', 'description', 'url', 'license', 'category', 'parent'),
	'rpm': ('name', 'version', 'release', 'arch', 'repo', 'dist', 'epoch'),
}

dataset = {
	'spec': { 'specname': 'varchar(12) unique primary key', },
#	'pkg' : {'filename': 'varchar(25) unique primary key', },
	'info': { 'name': 'varchar(10) unique primary key', },
}

def sqlcreate(name):
	'Return a database create SQL statement'
	str = 'create table %s ( ' % name
	for key in headers[name]:
		if dataset.has_key(name) and dataset[name].has_key(key):
			str += '%s %s,' % (key, dataset[name][key])
		else:
			str += '%s varchar(10), ' % key
	return str.rstrip(', ') + ' )'

def sqlinsert(name):
	'Return a database insert SQL statement'
	str = 'insert into %s ( ' % name
	for key in headers[name]: str += '%s, ' % key
	str = str.rstrip(', ') + ' ) values ( '
	for key in headers[name]: str += '"%%(%s)s", ' % key
	return str.rstrip(', ') + ' )'

def opendb():
	con = sqlite.connect(dbase)
	cur = con.cursor()
	return (con, cur)

def createtb(cur, name, create=False):
	'Open a database and return references'
	try:
		cur.execute('drop table "%s"' % name)
	except Exception ,e:
		print e
	cur.execute(sqlcreate(name))

def insertrec(cur, name, rec):
	'Insert a record in a database'
	### Convert unicode to UTF-8
	for key in rec.keys():
		if isinstance(rec[key], types.UnicodeType):
			rec[key] = rec[key].encode('utf-8')
	cur.execute(sqlinsert(name) % rec)
