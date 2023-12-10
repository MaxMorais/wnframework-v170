import webnotes
import webnotes.utils

class FrameworkServer:
	"""
	   Connect to a remote server via HTTP (webservice).
	   
	   * [remote_host] is the the address of the remote server
	   * [path] is the path of the Framework (excluding index.py)
	"""
	def __init__(self, remote_host, path, user='', password='', account='', cookies=None, opts=None, https = 0):
		# validate
		if not (remote_host and path):
			raise Exception("Server address and path necessary")

		if not ((user and password) or (cookies)):
			raise Exception("Either cookies or user/password necessary")
	
		#self.remote_host = remote_host
		#self.path = path
		self.remote_host = 'http://localhost:8000/wnframework/v170/'
		self.path = path
		self.cookies = cookies or {}
		self.webservice_method='POST'
		self.account = account
		self.account_id = None
		self.https = https
		self.conn = None

		# login
		if not cookies:
			args = { 'usr': user, 'pwd': password, 'acx': account }
			
			if opts:
				args.update(opts)
			
			res = self.http_get_response('login', args)
		
			ret = res.read()
			try:
				ret = eval(ret)
			except Exception as e:
				webnotes.msgprint(ret)
				raise Exception(e)
				
			if ret.get('message') and ret.get('message')!='Logged In':
				raise Exception(ret.get('message'))
				
			if ret.get('exc'):
				raise Exception(ret.get('exc'))
				
			self._extract_cookies(res)

			self.account_id = self.cookies.get('account_id')
			self.sid = self.cookies.get('sid')
			
			self.login_response = res
			self.login_return = ret

	# -----------------------------------------------------------------------------------------

	def http_get_response(self, method, args):
		"""
		Run a method on the remote server, with the given arguments
		"""
		# get response from remote server
	
		import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, os

		args['cmd'] = method
		if self.path.startswith('/'): self.path = self.path[1:]
				
		protocol = self.https and 'https://' or 'http://'
		req = urllib.request.Request(protocol + os.path.join(self.remote_host, self.path, 'index.py'), urllib.parse.urlencode(args))
		for key in self.cookies:
			req.add_header('cookie', '; '.join(['%s=%s' % (key, self.cookies[key]) for key in self.cookies]))
		return urllib.request.urlopen(req)

	# -----------------------------------------------------------------------------------------
	
	def _extract_cookies(self, res):
		import http.cookies
		cookies = http.cookies.SimpleCookie()
		cookies.load(res.headers.get('set-cookie'))
		for c in list(cookies.values()):
			self.cookies[c.key] = c.value.rstrip(',')

	# -----------------------------------------------------------------------------------------


	def runserverobj(self, doctype, docname, method, arg=''):
		"""
		Returns the response of a remote method called on a system object specified by [doctype] and [docname]
		"""
		res = self.http_get_response('runserverobj', args = {
			'doctype':doctype
			,'docname':docname
			,'method':method
			,'arg':arg
		})
		ret = eval(res.read())
		if ret.get('exc'):
			raise Exception(ret.get('exc'))
		return ret
	
	# -----------------------------------------------------------------------------------------
			
	def run_method(self, method, args):
		res = self.http_get_response(method, args)
		ret = eval(res.read())
		if ret.get('exc'):
			raise Exception(ret.get('exc'))
		return ret
