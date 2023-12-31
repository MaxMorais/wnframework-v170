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


class DocType:
  def __init__(self,doc,doclist=[]):
    self.doc, self.doclist = doc,doclist

  #--------------------get naming series from sales invoice-----------------
  def get_series(self):
    res = sql("select options from [tabDocField] where parent='Receivable Voucher' and fieldname = 'naming_series'")
    return res and cstr(res[0][0]) or ''
  
  def validate(self):
    res = sql("select name, user from [tabPOS Setting] where ifnull(user, '') = '%s' and name != '%s' and company = '%s'" % (self.doc.user, self.doc.name, self.doc.company))
    if res:
      if res[0][1]:
        msgprint("POS Setting '%s' already created for user: '%s' and company: '%s'"%(res[0][0], res[0][1], self.doc.company), raise_exception=1)
      else:
        msgprint("Global POS Setting already created - %s for this company: '%s'" % (res[0][0], self.doc.company), raise_exception=1)
