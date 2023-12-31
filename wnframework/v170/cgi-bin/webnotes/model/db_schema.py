"""
Syncs a database table to the [DocType] (metadata)

.. note:: This module is only used internally

"""
import os
import webnotes

type_map = {
	'currency':		('REAL', '')
	,'int':			('INTEGER', '11')
	,'float':		('REAL', '')
	,'check':		('INTEGER NOT NULL DEFAULT 0', '')
	,'small text':	('TEXT', '')
	,'long text':	('TEXT', '')
	,'code':		('TEXT', '')
	,'text editor':	('TEXT', '')
	,'date':		('TEXT', '')
	,'time':		('TEXT', '')
	,'text':		('TEXT', '')
	,'data':		('TEXT', '')
	,'link':		('TEXT', '')
	,'password':	('TEXT', '')
	,'select':		('TEXT', '')
	,'read only':	('TEXT', '')
	,'blob':		('TEXT', '')
}

default_columns = ['name', 'creation', 'modified', 'modified_by', 'owner', 'docstatus', 'parent',\
	 'parentfield', 'parenttype', 'idx']

default_shortcuts = ['_Login', '__user', '_Full Name', 'Today', '__today']


from webnotes.utils import cint

# -------------------------------------------------
# Class database table
# -------------------------------------------------

class DbTable:
	def __init__(self, doctype, prefix = 'tab'):
		self.doctype = doctype
		self.name = prefix + doctype
		self.columns = {}
		self.current_columns = {}
		
		# lists for change
		self.add_column = []
		self.change_type = []
		self.add_index = []
		self.drop_index = []
		self.set_default = []
		
		# load
		self.get_columns_from_docfields()

	def create(self):
		add_text = ''
		index_text = ''
		
		# columns
		t = self.get_column_definitions()
		if t: add_text += ',\n'.join(self.get_column_definitions())
		
		# index
		t = self.get_index_definitions()
		if t: index_text += '\n'.join(self.get_index_definitions()) + ';\n'
	
		# create table
		sql = """-- %(name)s
DROP TABLE IF EXISTS [%(name)s];
CREATE TABLE IF NOT EXISTS [%(name)s] (
	[name] TEXT NOT NULL UNIQUE PRIMARY KEY,
	[creation] TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	[modified] TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	[modified_by] TEXT,
	[owner] TEXT,
	[docstatus] INTEGER NOT NULL DEFAULT 0,
	[parent] TEXT,
	[parentfield] TEXT,
	[parenttype] TEXT,
	[idx] INTEGER,
	%(add_text)s
);
DROP INDEX IF EXISTS [idx_%(name)s_parent];
CREATE INDEX [idx_%(name)s_parent] ON [%(name)s]([parent]);
%(index_text)s""" % {"name": self.name, "add_text": add_text, "index_text": index_text}
		try:
			webnotes.conn.script(sql)
		except:
			print(sql)

	def get_columns_from_docfields(self):
		fl = webnotes.conn.sql("SELECT * FROM tabDocField WHERE parent = ?" , (self.doctype,), as_dict = 1)

		for f in fl:
			if f['fieldname'] and not f.get('no_column'):
				self.columns[f['fieldname']] = DbColumn(self, f['fieldname'], f['fieldtype'], f.get('length'), f['default'], f['search_index'], f['options'])
	
	def get_columns_from_db(self):
		self.show_columns = webnotes.conn.sql("PRAGMA table_info([%s])" % self.name)
		for c in self.show_columns:
			self.current_columns[c[1]] = {'name': c[1], 'type':c[2], 'index':c[4], 'default':c[3]}
	
	def get_column_definitions(self):
		column_list = [] + default_columns
		ret = []
		for k in list(self.columns.keys()):
			if k not in column_list:
				d = self.columns[k].get_definition()
				if d:
					ret.append('\t['+ k+ '] ' + d)
					column_list.append(k)
		return ret
	
	def get_index_definitions(self):
		ret = []
		for k in list(self.columns.keys()):
			if type_map.get(self.columns[k].fieldtype) and type_map.get(self.columns[k].fieldtype.lower())[0] not in ('text', 'blob'):
				ret.append(f'DROP INDEX IF EXISTS [idx_tab{self.name}_{k}]')
				ret.append(f'CREATE INDEX IF NOT EXISTS [idx_tab{self.name}_{k}] ON [{self.name}]([{k}])')
		return ret


	# GET foreign keys
	def get_foreign_keys(self):
		fk_list = []
		res = webnotes.conn.sql("select sql from sqlite_master where name=?", (self.name,))
		if not res:
			return fk_list
		
		txt = res[0][1]
		for line in txt.split('\n'):
			if line.strip().startswith('CONSTRAINT') and line.find('FOREIGN')!=-1:
				try:
					fk_list.append((line.split('[')[3], line.split(']')[1]))
				except IndexError as e:
					pass

		return fk_list

	# Drop foreign keys
	def drop_foreign_keys(self):
		if not self.drop_foreign_key:
			return

		fk_list = self.get_foreign_keys()
		
		# make dictionary of constraint names
		fk_dict = {}
		for f in fk_list:
			fk_dict[f[0]] = f[1]
			
		# drop
		for col in self.drop_foreign_key:
			webnotes.conn.sql("set foreign_key_checks=0")
			webnotes.conn.sql("alter table [%s] drop foreign key [%s]" % (self.name, fk_dict[col.fieldname]))
			webnotes.conn.sql("set foreign_key_checks=1")
		
	def sync(self):
		if not self.name in DbManager(webnotes.conn).get_tables_list(webnotes.conn.cur_db_name):
			self.create()
		else:
			self.alter()
	
	def alter(self):
		self.get_columns_from_db()
		for col in list(self.columns.values()):
			col.check(self.current_columns.get(col.fieldname, None))

		for col in self.add_column:
			webnotes.conn.sql("alter table [%s] add column [%s] %s" % (self.name, col.fieldname, col.get_definition()))

		#for col in self.change_type:
			
			#sql = "alter table [%s] change [%s] [%s] %s" % (self.name, col.fieldname, col.fieldname, col.get_definition())
			#print(sql);
			#webnotes.conn.sql(sql)

		for col in self.add_index:
			webnotes.conn.sql("create index if not exists [idx_%(name)s_%(col)s] ON [%(name)s]([%(col)s])" % {
				'name': self.name,
				'col': col.fieldname
			})

		for col in self.drop_index:
			if col.fieldname != 'name': # primary key
				webnotes.conn.sql(
					'drop index if exists [idx_%(name)s_%(col)s];' % {
						'name': self.name,
						'col': col.fieldname
					}
				)

		#for col in self.set_default:
		#	webnotes.conn.sql("alter table [%s] alter [%s] %s" % (self.name, col.fieldname, '%s'), col.default)


# -------------------------------------------------
# Class database column
# -------------------------------------------------

class DbColumn:
	def __init__(self, table, fieldname, fieldtype, length, default, set_index, options):
		self.table = table
		self.fieldname = fieldname
		self.fieldtype = fieldtype
		self.length = length
		self.set_index = set_index
		self.default = default
		self.options = options

	def get_definition(self, with_default=1):
		d = type_map.get(self.fieldtype.lower())

		if not d:
			return
			
		ret = d[0]
		if d[1]:
			ret += '(' + d[1] + ')'
		if with_default and self.default and (self.default not in default_shortcuts):
			ret += ' default "' + self.default.replace('"', '\"') + '"'
		return ret
		
	def check(self, current_def):
		column_def = self.get_definition(0)

		# no columns
		if not column_def:
			return
		
		# to add?
		if not current_def:
			self.fieldname = validate_column_name(self.fieldname)
			self.table.add_column.append(self)
			return

		# type
		if current_def['type'] != column_def:
			self.table.change_type.append(self)
		
		# index
		else:
			if (current_def['index'] and not self.set_index):
				self.table.drop_index.append(self)
			
			if (not current_def['index'] and self.set_index and not (column_def in ['text','blob'])):
				self.table.add_index.append(self)
		
		# default
		if (self.default and (current_def['default'] != self.default) and (self.default not in default_shortcuts) and not (column_def in ['text','blob'])):
			self.table.set_default.append(self)


class DbManager:
	"""
	Basically, a wrapper for oft-used mysql commands. like show tables,databases, variables etc... 

	#TODO:
		0.  Simplify / create settings for the restore database source folder 
		0a. Merge restore database and extract_sql(from webnotes_server_tools).
		1. Setter and getter for different mysql variables.
		2. Setter and getter for mysql variables at global level??
	"""	
	def __init__(self,conn):
		"""
		Pass root_conn here for access to all databases.
		"""
		if conn:
			self.conn = conn
		

	def get_variables(self,regex):
		"""
		Get variables that match the passed pattern regex
		"""
		return list(self.conn.sql("SHOW VARIABLES LIKE '%s'"%regex))


	def drop_all_databases(self):
		"""
		Danger: will delete all databases except test,mysql.
		"""
		db_list = self.get_database_list()
		for db in db_list:
			self.drop_database(db)
			
	def get_table_schema(self,table):
		"""
		Just returns the output of Desc tables.
		"""
		return list(self.conn.sql("DESC %s"%table))
		
			
	def get_tables_list(self,target):	
		"""
		
		"""
		try:
			self.conn.use(target)
			res = self.conn.sql("select name from sqlite_master where type = 'table';")
			table_list = []
			for table in res:
				table_list.append(table[0])
			return table_list

		except Exception as e:
			raise e

	def create_user(self,user,password):
		#Create user if it doesn't exist.
		return 
		try:
			if password:
				self.conn.sql("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (user[:16], password))
			else:
				self.conn.sql("CREATE USER '%s'@'localhost';"%user[:16])
		except Exception as e:
			raise e


	def delete_user(self,target):
		# delete user if exists
		return 
		try:
			self.conn.sql("DROP USER '%s'@'localhost';" % target)
		except Exception as e:
			if e.args[0]==1396:
				pass
			else:
				raise e

	def create_database(self,target):
		return 
		try:
			self.conn.sql("CREATE DATABASE IF NOT EXISTS [%s] ;" % target)
		except Exception as e:
			raise e


	def drop_database(self,target):
		return 
		try:
			self.conn.sql("DROP DATABASE IF EXISTS [%s];"%target)
		except Exception as e:
			raise e

	def grant_all_privileges(self,target,user):
		return 
		try:
			self.conn.sql("GRANT ALL PRIVILEGES ON [%s] . * TO '%s'@'localhost';" % (target, user))
		except Exception as e:
			raise e

	def grant_select_privilges(self,db,table,user):
		return 
		try:
			if table:
				self.conn.sql("GRANT SELECT ON %s.%s to '%s'@'localhost';" % (db,table,user))
			else:
				self.conn.sql("GRANT SELECT ON %s.* to '%s'@'localhost';" % (db,user))
		except Exception as e:
			raise e

	def flush_privileges(self):
		return 
		try:
			self.conn.sql("FLUSH PRIVILEGES")
		except Exception as e:
			raise e


	def get_database_list(self):
		try:
			db_list = []
			ret_db_list = self.conn.sql("SHOW DATABASES")
			for db in ret_db_list:
				if db[0] not in ['information_schema', 'mysql', 'test', 'accounts']:
					db_list.append(db[0])
			return db_list
		except Exception as e:
			raise e

	def restore_database(self,target,source,root_password):
		import webnotes.defs
		mysql_path = getattr(webnotes.defs, 'mysql_path', None)
		#mysql = mysql_path and os.path.join(mysql_path, 'mysql') or 'mysql'
		mysql = 'sqlite3'
		
		try:
		#	ret = os.system("%s -u root -p%s %s < %s"%(mysql, root_password, target, source))
			ret = os.system(f"{mysql} < {source}");
		except Exception as e:
			raise e
		

	def drop_table(self,table_name):
		try:
			self.conn.sql("DROP TABLE IF EXISTS [%s]"%(table_name))
		except Exception as e:
			raise e	

	def set_transaction_isolation_level(self,scope='SESSION',level='READ COMMITTED'):
		#Sets the transaction isolation level. scope = global/session
		return
		try:
			self.conn.sql("SET %s TRANSACTION ISOLATION LEVEL %s"%(scope,level))
		except Exception as e:
			raise e



# -------------------------------------------------
# validate column name to be code-friendly
# -------------------------------------------------

def validate_column_name(n):
	n = n.replace(' ','_').strip().lower()
	import re
	if not re.match("[a-zA-Z_][a-zA-Z0-9_]*$", n):
		webnotes.msgprint('err:%s is not a valid fieldname.<br>A valid name must contain letters / numbers / spaces.<br><b>Tip: </b>You can change the Label after the fieldname has been set' % n)
		raise Exception
	return n

# -------------------------------------------------
# sync table - called from form.py
# -------------------------------------------------

def updatedb(dt, archive=0):
	"""
	Syncs a [DocType] to the table
	   * creates if required
	   * updates columns
	   * updates indices
	"""
	res = webnotes.conn.sql("select ifnull(issingle, 0) from tabDocType where name=%s", dt)
	if not res:
		raise Exception('Wrong doctype "%s" in updatedb' % dt)
	
	if not res[0][0]:
		webnotes.conn.commit()
		tab = DbTable(dt, archive and 'arc' or 'tab')
		tab.sync()
		webnotes.conn.begin()

# patch to remove foreign keys
# ----------------------------

def remove_all_foreign_keys():
	from sqlite3 import OperationalError

	webnotes.conn.sql("set foreign_key_checks = 0")
	webnotes.conn.commit()
	for t in webnotes.conn.sql("select name from tabDocType where ifnull(issingle,0)=0"):
		dbtab = webnotes.model.db_schema.DbTable(t[0])
		try:
			fklist = dbtab.get_foreign_keys()
		except OperationalError as e:
			if 'no such table' in str(e):
				fklist = []
			else:
				raise e
				
		for f in fklist:
			webnotes.conn.sql("alter table [tab%s] drop foreign key [%s]" % (t[0], f[1]))
