"""
	Create a database from scratch (wip)
"""

class DatabaseInstance:

	def __init__(self, conn = None,db_name = None):
		self.conn = conn
		self.db_name = db_name
		
		
#	def setup(self):
#		self.create_db_and_user()
#		self.create_base_tables()
#		self.import_system_module()
#		self.setup_users()
		
	def create_db_and_user(self):
		import webnotes.defs
		
		return

		# create user and db
		self.conn.sql("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'" % (self.db_name, webnotes.defs.db_password))
		self.conn.sql("CREATE DATABASE IF NOT EXISTS [%s] ;" % self.db_name)
		self.conn.sql("GRANT ALL PRIVILEGES ON [%s] . * TO '%s'@'localhost';" % (self.db_name, self.db_name))
		self.conn.sql("FLUSH PRIVILEGES")
		self.conn.sql("SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED;")
		self.conn.sql("USE %s"%self.db_name)
		
		
	
		
	
	def create_base_tables(self):
		self.create_singles()
		self.create_sessions()
		self.create_doctypecache()
		self.create_role()
		self.create_docfield()
		self.create_docperm()
		self.create_docformat()
		self.create_doctype()

	def import_system_module(self):
		docs = [
			['DocType','Role']
			,['Role','Administrator']
			,['Role','Guest']
			,['Role','All']
			,['DocType','DocPerm']
			,['DocType','DocFormat']
			,['DocType','DocField']
			,['DocType','DocType']
			,['DocType','DefaultValue']
			,['DocType','Profile']
			,['DocType','UserRole']
		]
		
		# import in sequence
		for d in docs:
			import_module.import_from_files(record_list=[['System',d[0],d[1]]])
		
		# import all
		import_module.import_from_files([['System']])
			

	# singles
	# ------------------------------------------------------

	def create_singles(self):
		self.conn.script("""-- tabSingles
DROP TABLE IF EXISTS [tagSingles];
CREATE TABLE IF NOT EXISTS [tabSingles] (
	[doctype] TEXT,
	[field] TEXT,
	[value] TEXT
);

DROP INDEX IF EXISTS [idx_tabSingles_doctype];
CREATE INDEX [idx_tabSingles_doctype] ON tabSingles(doctype);
""")
	
	# sessions
	# ------------------------------------------------------

	def create_sessions(self):
		self.conn.script("""-- tabSessions
DROP TABLE IF EXISTS [tabSessions];
CREATE TABLE IF NOT EXISTS [tabSessions] (
	[user] TEXT,
	[sid] TEXT,
	[sessiondata] TEXT,
	[ipaddress] TEXT,
	[lastupdate] TEXT,
	[status] TEXT
);""")

	# doc type cache
	# ------------------------------------------------------

	def create_doctypecache(self):
		self.conn.script("""-- __DocTypeCache
DROP TABLE IF EXISTS [__DocTypeCache];
CREATE TABLE IF NOT EXISTS [__DocTypeCache] (
	[name] TEXT NOT NULL UNIQUE PRIMARY KEY,
	[modified] TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	[content]
);
""")
		
		

	# Role
	# ------------------------------------------------------

	def create_role(self):
		self.conn.script("""-- tabRole
DROP TABLE IF EXISTS [tabRole];
CREATE TABLE IF NOT EXISTS [tabRole](
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
	[role_name] TEXT,
	[module] TEXT
);

DROP INDEX IF EXISTS [idx_tabRole_parent];
CREATE INDEX [idx_tabRole_parent] ON [tabRole]([parent]);""")

	# DocField
	# ------------------------------------------------------

	def create_docfield(self):
		self.conn.script("""-- tabDocField
DROP TABLE IF EXISTS [tabDocField];
CREATE TABLE IF NOT EXISTS [tabDocField](
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
	[fieldname] TEXT,
	[label] TEXT,
	[oldfieldname] TEXT,
	[fieldtype] TEXT,
	[options] TEXT,
	[search_index] TEXT,
	[hidden] INTEGER DEFAULT 0,
	[print_hide] INTEGER DEFAULT 0,
	[report_hide] INTEGER DEFAULT 0,
	[reqd] INTEGER DEFAULT 0,
	[no_copy] INTEGER DEFAULT 0,
	[allow_on_submit] INTEGER DEFAULT 0,
	[trigger] TEXT,
	[depends_on] TEXT,
	[permlevel] INTEGER,
	[width] TEXT,
	[default] TEXT,
	[description] TEXT,
	[colour] TEXT,
	[icon] TEXT,
	[in_filter] INTEGER DEFAULT 0
);

DROP INDEX IF EXISTS [idx_tabDocField_parent];
DROP INDEX IF EXISTS [idx_tabDocField_label];
DROP INDEX IF EXISTS [idx_tabDocField_fieldtype];
DROP INDEX IF EXISTS [idx_tabDocField_fieldname];

CREATE INDEX [idx_tabDocField_parent] ON [tabDocField]([parent]);
CREATE INDEX [idx_tabDocField_label] ON [tabDocField]([label]);
CREATE INDEX [idx_tabDocField_fieldtype] ON [tabDocField]([fieldtype]);
CREATE INDEX [idx_tabDocField_fieldname] ON [tabDocField]([fieldname]);""")

	# DocPerm
	# ------------------------------------------------------

	def create_docperm(self):
		self.conn.script("""-- tabDocPerm
DROP TABLE IF EXISTS [tabDocPerm];
CREATE TABLE IF NOT EXISTS [tabDocPerm](
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
	[permlevel] INTEGER,
	[role] TEXT,
	[match] TEXT,
	[read] INTEGER NOT NULL DEFAULT 0,
	[write] INTEGER NOT NULL DEFAULT 0,
	[create] INTEGER NOT NULL DEFAULT 0,
	[submit] INTEGER NOT NULL DEFAULT 0,
	[cancel] INTEGER NOT NULL DEFAULT 0,
	[amend] INTEGER NOT NULL DEFAULT 0,
	[execute] INTEGER NOT NULL DEFAULT 0
);

DROP INDEX IF EXISTS [idx_tabDocPerm_parent];
CREATE INDEX idx_tabDocPerm_parent ON [tabDocPerm]([parent]);""")
		
	# DocFormat
	# ------------------------------------------------------

	def create_docformat(self):
		self.conn.script("""-- tabDocFormat
DROP TABLE IF EXISTS [tabDocFormat];
CREATE TABLE IF NOT EXISTS [tabDocFormat](
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
	[format] TEXT
);

DROP INDEX IF EXISTS [idx_tabDocFormat_parent];
CREATE INDEX [idx_tabDocFormat_parent] ON [tabDocFormat]([parent]);""")

	# DocType
	# ------------------------------------------------------

	def create_doctype(self):
		self.conn.script("""-- tabDocType
DROP TABLE IF EXISTS [tabDocType];
CREATE TABLE IF NOT EXISTS [tabDocType] (
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
	[search_fields] TEXT,
	[issingle] INTEGER NOT NULL DEFAULT 0,
	[istable] INTEGER NOT NULL DEFAULT 0,
	[version] INTEGER,
	[module] TEXT,
	[autoname] TEXT,
	[name_case] TEXT,
	[description] TEXT,
	[colour] TEXT,
	[read_only] INTEGER NOT NULL DEFAULT 0,
	[in_create] INTEGER NOT NULL DEFAULT 0,
	[show_in_menu] INTEGER NOT NULL DEFAULT 0,
	[menu_index] INTEGER,
	[parent_node] TEXT,
	[smallicon] TEXT,
	[allow_print] INTEGER NOT NULL DEFAULT 0,
	[allow_email] INTEGER NOT NULL DEFAULT 0,
	[allow_copy] INTEGER NOT NULL DEFAULT 0,
	[allow_rename] INTEGER NOT NULL DEFAULT 0,
	[hide_toolbar] INTEGER NOT NULL DEFAULT 0,
	[hide_heading] INTEGER NOT NULL DEFAULT 0,
	[allow_attach] INTEGER NOT NULL DEFAULT 0,
	[use_template] INTEGER NOT NULL DEFAULT 0,
	[max_attachments] INTEGER,
	[section_style] TEXT,
	[client_script] TEXT,
	[client_script_core] TEXT,
	[server_code] TEXT,
	[server_code_core] TEXT,
	[server_code_compiled] TEXT,
	[client_string] TEXT,
	[server_code_error] TEXT,
	[print_outline] TEXT,
	[dt_template] TEXT,
	[is_transaction_doc] INTEGER NOT NULL DEFAULT 0,
	[change_log] TEXT,
	[read_only_onload] INTEGER NOT NULL DEFAULT 0
);

DROP INDEX IF EXISTS [idx_tabDocType_parent]; 
CREATE INDEX [idx_tabDocType_parent] ON [tabDocType]([parent]);""")
		
	def create_module_def(self):
		self.conn.script("""-- tabModule Def
DROP TABLE IF EXISTS [tabModule Def];
CREATE TABLE IF NOT EXISTS [tabModule Def](
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
	[module_name] TEXT,
	[doclist] TEXT
);
DROP INDEX IF EXISTS [idx_tabModule Def_parent];
CREATE INDEX [idx_tabModule Def_parent] ON [tabModule Def]([parent]);""")


	def post_cleanup(self):
		#self.conn.sql("use %s;" % self.db_name)
		self.conn.sql("update tabProfile set password = password('admin') where name='Administrator'")
		self.conn.sql("update tabDocType set server_code_compiled = NULL")	
