#!/home/tmx-dev-05/Downloads/wn/env/bin/python

def getTraceback():
	import sys, traceback, string

	type, value, tb = sys.exc_info()
	body = "Traceback (innermost last):\n"
	list = traceback.format_tb(tb, None) + traceback.format_exception_only(type, value)
	body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])

	return body	

try:

	import sys, os, cgi

	sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cgi-bin'))

	import webnotes
	import webnotes.defs

	webnotes.form = cgi.FieldStorage()
	for each in list(webnotes.form.keys()):
		webnotes.form_dict[each] = webnotes.form.getvalue(each)
	if webnotes.form.getvalue('cmd'):
		# AJAX Call
		import webnotes.handler
	else:
		# Page Call
		import webnotes.auth
		import webnotes.widgets.page_body

		webnotes.auth.HTTPRequest()

		print("Content-Type: text/html")

		# print cookies, if there ar additional cookies defined during the request, add them here
		if webnotes.cookies or webnotes.add_cookies:
			for c in list(webnotes.add_cookies.keys()):
				webnotes.cookies[c] = webnotes.add_cookies[c]
			
			print(webnotes.cookies)

		print()
		print(webnotes.widgets.page_body.get())

except Exception as e:
	print("Content-Type: text/html")
	print()
	print(getTraceback().replace('\n','<br>'))
	print(e)
