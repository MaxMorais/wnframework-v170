import webnotes
from webnotes.utils import cint

form = webnotes.form

from webnotes.utils.email_lib import get_footer
from webnotes.utils.email_lib.send import EMail

class FormEmail:
	"""
		Represents an email sent from a Form
	"""
	def __init__(self):
		"""
			Get paramteres from the cgi form object
		"""
		self.__dict__.update(webnotes.form_dict)		

		self.recipients = None
		if self.sendto:
			self.recipients = self.sendto.replace(';', ',')
			self.recipients = self.recipients.split(',')

	def update_contacts(self):
		"""
			Add new email contact to database
		"""
		import webnotes
		from webnotes.model.doc import Document
		from sqlite3 import OperationalError

		for r in self.recipients:
			r = r.strip()
			try:
				if not webnotes.conn.sql("select email_id from tabContact where email_id=%s", r):
					d = Document('Contact')
					d.email_id = r
					d.save(1)
			except OperationalError as e:
				if 'no such table' in str(e): pass # no table
				else: raise e
	
	def make_full_links(self):
		"""
			Adds server name the relative links, so that images etc can be seen correctly
		"""
		# only domain
		if not self.__dict__.get('full_domain'):
			return
			
		def make_full_link(match):
			import os
			link = match.group('name')
			if not link.startswith('http'):
				link = os.path.join(self.full_domain, link)
			return 'src="%s"' % link

		import re
		p = re.compile('src[ ]*=[ ]*" (?P<name> [^"]*) "', re.VERBOSE)
		self.body = p.sub(make_full_link, self.body)

		p = re.compile("src[ ]*=[ ]*' (?P<name> [^']*) '", re.VERBOSE)
		self.body = p.sub(make_full_link, self.body)

	def get_form_link(self):
		"""
			Returns publicly accessible form link
		"""
		public_domain = webnotes.conn.get_value('Control Panel', None, 'public_domain')
		from webnotes.utils.encrypt import encrypt

		if not public_domain:
			return ''

		args = {
			'dt': self.dt, 
			'dn':self.dn, 
			'acx': webnotes.conn.get_value('Control Panel', None, 'account_id'),
			'server': public_domain,
			'akey': encrypt(self.dn)
		}
		return '<div>If you are unable to view the form below <a href="http://%(server)s/index.py?page=Form/%(dt)s/%(dn)s&acx=%(acx)s&akey=%(akey)s">click here to see it in your browser</div>' % args

	def set_attachments(self):
		"""
			Set attachments to the email from the form
		"""

		from sqlite3 import OperationalError

		al = []
		try:
			al = webnotes.conn.sql('select file_list from [tab%s] where name="%s"' % (form.getvalue('dt'), form.getvalue('dn')))
			if al:
				al = (al[0][0] or '').split('\n')
		except OperationalError as e:
			if 'no such table' in str(e):
				pass # no attachments in single types!
			else:
				raise Exception(e)
		return al
	
	def build_message(self):
		"""
			Builds the message object
		"""

		self.email = EMail(self.sendfrom, self.recipients, self.subject, alternative = 1)

		from webnotes.utils.email_lib.html2text import html2text

		self.make_full_links()

		# message
		if not self.__dict__.get('message'):
			self.message = 'Please find attached %s: %s\n' % (self.dt, self.dn)

		html_message = text_message = self.message.replace('\n','<br>')
		
		# separator
		html_message += '<div style="margin:17px 0px; border-bottom:1px solid #AAA"></div>'

		# form itself (only in the html message)
		html_message += self.body

		# form link
		html_message += self.get_form_link()
		text_message += self.get_form_link()

		# footer
		footer = get_footer()
		if footer: 
			html_message += footer
			text_message += footer

		# message as text
		self.email.set_text(html2text(text_message))
		self.email.set_html(html_message)
					
	def send(self):
		"""
			Send the form with html attachment
		"""

		if not self.recipients:
			webnotes.msgprint('No one to send to!')
			return
			
		self.build_message()
		
		# print format (as attachment also - for text-only clients)
		self.email.add_attachment(self.dn.replace(' ','').replace('/','-') + '.html', self.body)

		# attachments
		if cint(self.with_attachments):
			for a in self.set_attachments():
				a and self.email.attach(a.split(',')[0])

		# cc
		if self.cc:
			self.email.cc = [self.cc]
		
		self.email.send(send_now=1)
		webnotes.msgprint('Sent')