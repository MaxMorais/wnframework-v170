"""
This is where all the plug-in code is executed. The standard method for DocTypes is declaration of a 
standardized [DocType] class that has the methods of any DocType. When an object is instantiated using the
[get_obj] method, it creates an instance of the [DocType] class of that particular DocType and sets the 
[doc] and [doclist] attributes that represent the fields (properties) of that record.

methods in following modules are imported for backward compatibility

	* webnotes.*
	* webnotes.utils.*
	* webnotes.model.doc.*
	* webnotes.model.doclist.*
"""
custom_class = '''
# Please edit this list and import only required elements
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, getdate, has_common, month_name, now, nowdate, replace_newlines, sendmail, set_default, str_esc_quote, user_format, validate_email_add
from webnotes.model import db_exists
from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname, SuperDocType
from webnotes.model.doclist import getlist, copy_doclist
from webnotes.model.code import get_obj, get_server_obj, run_server_obj, updatedb, check_syntax
from webnotes import session, form, is_testing, msgprint, errprint

set = webnotes.conn.set
sql = webnotes.conn.sql
get_value = webnotes.conn.get_value
in_transaction = webnotes.conn.in_transaction
convert_to_lists = webnotes.conn.convert_to_lists

# -----------------------------------------------------------------------------------------

class CustomDocType(DocType):
  def __init__(self, doc, doclist):
	DocType.__init__(self, doc, doclist)
'''


#=================================================================================
# execute a script with a lot of globals - deprecated
#=================================================================================

def execute(code, doc=None, doclist=[]):
	"""
	Execute the code, if doc is given, then return the instance of the [DocType] class created
	"""
	# functions used in server script of DocTypes
	# --------------------------------------------------	
	from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, generate_hash, getTraceback, get_defaults, get_first_day, get_last_day, getdate, has_common, month_name, now, nowdate, replace_newlines, sendmail, set_default, str_esc_quote, user_format, validate_email_add
	from webnotes.model import db_exists
	from webnotes.model.doc import Document, addchild, removechild, getchildren, make_autoname, SuperDocType
	from webnotes.model.doclist import getlist, copy_doclist
	from webnotes import session, form, is_testing, msgprint, errprint

	import webnotes

	set = webnotes.conn.set
	sql = webnotes.conn.sql
	get_value = webnotes.conn.get_value
	in_transaction = webnotes.conn.in_transaction
	convert_to_lists = webnotes.conn.convert_to_lists
	if webnotes.user:
		get_roles = webnotes.user.get_roles
	locals().update({'get_obj':get_obj, 'get_server_obj':get_server_obj, 'run_server_obj':run_server_obj, 'updatedb':updatedb, 'check_syntax':check_syntax})
	version = 'v170'
	NEWLINE = '\n'
	BACKSLASH = '\\'

	# execute it
	# -----------------
	exec(code, locals())
	
	# if doc
	# -----------------
	if doc:
		d = DocType(doc, doclist)
		return d
		
	if locals().get('page_html'):
		return page_html

	if locals().get('out'):
		return out

#=================================================================================
# load the DocType class from module & return an instance
#=================================================================================

def get_custom_script(doctype, script_type):
	"""
		Returns custom script if set in doctype [Custom Script]
	"""
	from sqlite3 import OperationalError
	import webnotes
	try:
		custom_script = webnotes.conn.sql("select script from [tabCustom Script] where dt=%s and script_type=%s", (doctype, script_type))
	except OperationalError as e:
		if 'no such table' in str(e):
			return None
		else: raise e
			
	if custom_script and custom_script[0][0]:
		return custom_script[0][0]
		
def get_server_obj(doc, doclist = [], basedoctype = ''):
	"""
	Returns the instantiated [DocType] object. Will also manage caching & compiling
	"""
	# for test
	import webnotes
	from pydoc import locate
	#from importlib import import_module
	

	# get doctype details
	module = webnotes.conn.get_value('DocType', doc.doctype, 'module')
	
	# no module specified (must be really old), can't get code so quit
	if not module and doc.doctype != 'DocType':
		return
	elif doc.doctype == 'DocType':
		module = 'Core'
		
	module = module.replace(' ','_').lower()
	dt = doc.doctype.replace(' ','_').lower()

	# import
	DocType = locate(f'{module}.doctype.{dt}.{dt}.DocType')
	if not DocType:
		class DocType:
			def __init__(self, d, dl):
				self.doc, self.doclist = d, dl

	# custom?
	custom_script = get_custom_script(doc.doctype, 'Server')
	if custom_script:
		global custom_class		
		
		exec(custom_class + custom_script.replace('\t','  '), locals())
			
		return CustomDocType(doc, doclist)
	else:
		return DocType(doc, doclist)
	
#=================================================================================
# get object (from dt and/or dn or doclist)
#=================================================================================

def get_obj(dt = None, dn = None, doc=None, doclist=[], with_children = 0):
	"""
	   Returns the instantiated [DocType] object. Here you can pass the DocType and name (ID) to get the object.
	   If with_children is true, then all child records will be laoded and added in the doclist.
	"""	
	if dt:
		import webnotes.model.doc
		
		if not dn:
			dn = dt
		if with_children:
			doclist = webnotes.model.doc.get(dt, dn, from_get_obj=1)
		else:
			doclist = webnotes.model.doc.get(dt, dn, with_children = 0, from_get_obj=1)
		return get_server_obj(doclist[0], doclist)
	else:
		return get_server_obj(doc, doclist)
		
#=================================================================================
# get object and run method
#=================================================================================

def run_server_obj(server_obj, method_name, arg=None):
	"""
	   Executes a method ([method_name]) from the given object ([server_obj])
	"""
	if server_obj and hasattr(server_obj, method_name):
		if arg:
			return getattr(server_obj, method_name)(arg)
		else:
			return getattr(server_obj, method_name)()
	else:
		raise Exception('No method %s' % method_name)

#=================================================================================
# deprecated methods to keep v160 apps happy
#=================================================================================

def updatedb(doctype, userfields = [], args = {}):
	pass

def check_syntax(code):
	return ''

#===================================================================================
def get_code(module, dt, dn, extn, is_static=None, fieldname=None):
	from webnotes.modules import scrub, get_module_path
	import os, webnotes
	
	# get module (if required)
	if not module:
		module = webnotes.conn.sql("select module from [tab%s] where name=%s" % (dt,'%s'),dn)[0][0]

	# no module, quit
	if not module:
		return ''
	
	# file names
	if scrub(dt) in ('page','doctype','search_criteria'):
		dt, dn = scrub(dt), scrub(dn)

	# get file name
	fname = dn + '.' + extn
	if is_static:
		fname = dn + '_static.' + extn

	# code
	code = ''
	try:
		file = open(os.path.join(get_module_path(scrub(module)), dt, dn, fname), 'r')
		code = file.read()
		file.close()	
	except IOError as e:
		# no file, try from db
		if fieldname:
			code = webnotes.conn.get_value(dt, dn, fieldname)

	return code
