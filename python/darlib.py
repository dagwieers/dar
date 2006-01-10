import os, sqlite, types

dbase = 'darbase.sqlite'

headers = {
	'spec': ('name', 'authority', 'summary', 'epoch', 'version', 'release', 'license', 'category', 'url', 'description', 'upstream', 'parent'),
	'pkg': ('name', 'version', 'release', 'arch', 'repo', 'dist', 'parent', 'builder'),
	'info': ('name', 'summary', 'description', 'url', 'license', 'category', 'parent'),
	'rpm': ('name', 'version', 'release', 'arch', 'repo', 'dist', 'epoch'),
}

dataset = {
	'spec': { 'name': 'varchar(10) unique primary key', },
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

def opentb(con, name, create=False):
	'Open a database and return references'
	cur = con.cursor()
	if create:
		try: cur.execute('drop table "%s"' % name)
		except: pass
		cur.execute(sqlcreate(name))
	return cur

def inserttb(cur, name, rec):
	'Insert a record in a database'
	### Convert unicode to UTF-8
	for key in rec.keys():
		if isinstance(rec[key], types.UnicodeType):
			rec[key] = rec[key].encode('utf-8')
	cur.execute(sqlinsert(name) % rec)
