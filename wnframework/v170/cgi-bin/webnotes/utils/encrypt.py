"""
XTEA Block Encryption Algorithm
Author: Paul Chakravarti (paul_dot_chakravarti_at_gmail_dot_com)
License: Public Domain
""" 

def get_key():
	# Encryption key is datetime of creation of DocType, DocType"
	import webnotes
	return webnotes.conn.sql("select creation from tabDocType where name='DocType'")[0][0].strftime('%Y%m%d%H%M%s')[:16]

def encrypt(data, encryption_key = None):
	if not encryption_key:
		encryption_key = get_key()
	return crypt(encryption_key, data).encode('hex')

def decrypt(data, encryption_key = None):
	if not encryption_key:
		encryption_key = get_key()
	return crypt(encryption_key, data.decode('hex'))

def crypt(key,data,iv='\00\00\00\00\00\00\00\00',n=32):
	def keygen(key,iv,n):
		while True:
			iv = xtea_encrypt(key,iv,n)
			for k in iv:
				yield ord(k)
	xor = [ chr(x^y) for (x,y) in zip(list(map(ord,data)),keygen(key,iv,n)) ]
	return "".join(xor)

def xtea_encrypt(key,block,n=32,endian="!"):
	import struct
	v0,v1 = struct.unpack(endian+"2L",block)
	k = struct.unpack(endian+"4L",key)
	sum,delta,mask = 0,0x9e3779b9,0xffffffff
	for round in range(n):
		v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
		sum = (sum + delta) & mask
		v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
	return struct.pack(endian+"2L",v0,v1)
	
def xtea_decrypt(key,block,n=32,endian="!"):
	import struct

	v0,v1 = struct.unpack(endian+"2L",block)
	k = struct.unpack(endian+"4L",key)
	delta,mask = 0x9e3779b9,0xffffffff
	sum = (delta * n) & mask
	for round in range(n):
		v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
		sum = (sum - delta) & mask
		v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
	return struct.pack(endian+"2L",v0,v1)

