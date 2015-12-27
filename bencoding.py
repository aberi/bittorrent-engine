import sys
import getopt
import hashlib
import urllib

def usage():
	print "Usage: bit_client <torrent file>"

def is_int(c):
	o = ord(c)
	return (o >= 48 and o <= 57)

def bencode_parse_raw(text):
	if text[0] == 'l':
		return bencode_parse_list_raw(text)
	elif text[0] == 'd':
		return bencode_parse_dict_raw(text)
	elif text[0] == 'i':
		return bencode_parse_int_raw(text)
	else:
		try:
			(n_read, value) = bencode_parse_string_raw(text)
			return (n_read, value)
		except Exception:
			raise Exception("Parse Error: Bencoding must begin with l, d, or i (not strictly speaking)") 
	

# Parse a "unit" of bencoding.
def bencode_parse(text):
	if text[0] == 'l':
		return bencode_parse_list(text)
	elif text[0] == 'd':
		return bencode_parse_dict(text)
	elif text[0] == 'i':
		return bencode_parse_int(text)
	else:
		try:
			(n_read, value) = bencode_parse_string(text)
			return (n_read, value)
		except Exception:
			raise Exception("Parse Error: Bencoding must begin with l, d, or i (not strictly speaking)") 
	
def bencode_parse_list_raw(text):
	if text[0] != 'l':
		raise Exception("Lists must begin with \'l\'")

	index = 1
	a = ""			# Return value (accumulator)

	while text[index] != 'e':
		p = text[index:]
		(n_read, value) = bencode_parse_raw(p)
		a = "".join([a, value])
		index += n_read

	return (index + 1, 'l' + a + 'e') # Remember to skip the e that terminates the list!

def bencode_parse_list(text):
	if text[0] != 'l':
		raise Exception("Lists must begin with \'l\'")

	index = 1
	a = []			# Return value (accumulator)

	while text[index] != 'e':
		p = text[index:]
		(n_read, value) = bencode_parse(p)
		a.append(value)
		index += n_read

	return (index + 1, a) # Remember to skip the e that terminates the list!

def bencode_parse_string_raw(text):
	num_digits = 0

	while is_int(text[num_digits]):	
		num_digits += 1

	length = text[:num_digits]
		
	raw_data = text[:num_digits + 1 + int(length)]

	return (num_digits + 1 + int(length), raw_data) # length of string + ':' + string itself

def bencode_parse_string(text):
	num_digits = 0

	while is_int(text[num_digits]):	
		num_digits += 1

	length = text[:num_digits]
	content = text[num_digits + 1: num_digits + 1 + int(length)]

	return (num_digits + 1 + int(length), content) # length of string + ':' + string itself

def bencode_encode(k):
	if type(k) is int:
		return bencode_encode_int(k)
	elif type(k) is str:
		return bencode_encode_str(k)
	elif type(k) is list:
		return bencode_encode_list(k)
	elif type(k) is dict:
		return bencode_encode_dict(k)
	elif type(k) is tuple:
		(i, v) = k
		if type(v) is int:
			return bencode_encode_int(v)
		elif type(v) is str:
			return bencode_encode_string(v)
		elif type(v) is list:
			return bencode_encode_list(v)
		elif type(v) is dict:
			return bencode_encode_dict(v)
	else:
		raise Exception("Parse Error: Objects within the dict must be an int, str, list, or dict")	

def bencode_encode_int(i):
	return 'i' + str(i) + 'e'

def bencode_encode_str(s):
	return str(len(s)) + ':' + s

def bencode_encode_list(l):
	s = ""
	for e in l:
		s = s + bencode_encode(e)

	return 'l' + s + 'e'

def bencode_encode_dict(d):
	s = ""
	a = []
	for i in range(0, 2 * len(d.keys())):
		a.append(())
	for k in d.keys():
		bkey = bencode_encode(k)	
		(tod, value) = d[k]
		bvalue = bencode_encode(value)	
		a[2 * tod] = bkey
		a[2 * tod + 1] = bvalue
		
	return 'd' + "".join(a) + 'e'

def bencode_parse_dict_raw(text):
	if text[0] != 'd':
		raise Exception("Dicts must begin with \'d\'")
	index = 1
	d = "" 
	# Parse the next two entries together, because we have to place them in a KEY: VALUE pairing in the dictionary
	while text[index] != 'e':
		# Get key
		p = text[index:]
		(n_read, key) = bencode_parse_raw(p)
		index += n_read
		d = "".join([d,key])
		# Get corresponding value
		p = text[index:]
		(n_read, value) = bencode_parse_raw(p)
		index += n_read
		d = "".join([d,value])
		# Place in the dictionary
		
	return (index + 1, "d" + d + "e")

def bencode_no_tod(b):
	if type(b) is tuple:
		(tod, v) = b
		return bencode_no_tod(v)
	elif type(b) is list:
		for i in range(0, len(b)):
			b[i] = bencode_no_tod(b[i])
		return b
	elif type(b) is dict:
		return bencode_dict_no_tod(b)
	else:
		return b

def bencode_dict_no_tod(d):
	e = {}
	for k in d.keys():
		e[k] = bencode_no_tod(d[k])
	return e	

def bencode_parse_dict(text):
	if text[0] != 'd':
		raise Exception("Dicts must begin with \'d\'")
	index = 1
	d = {}
	tod = 0
	# Parse the next two entries together, because we have to place them in a KEY: VALUE pairing in the dictionary
	while text[index] != 'e':
		# Get key
		p = text[index:]
		(n_read, key) = bencode_parse(p)
		index += n_read
		# Get corresponding value
		p = text[index:]
		(n_read, value) = bencode_parse(p)
		index += n_read
		# Place in the dictionary
		d[key] = (tod, value)
		tod += 1
		
	return (index + 1, d)

def bencode_parse_int_raw(text):
	if text[0] != 'i':
		raise Exception("Integers must begin with \'i\'")
	i = text.index('e')
	if i == -1:	
		raise Exception("Parse Error: Integer must end with \'e\'")
	return (i + 1, text[:i + 1]) # 'i' + strlen(num_string) + 'e'
	
def bencode_parse_int(text):
	if text[0] != 'i':
		raise Exception("Integers must begin with \'i\'")
	i = text.index('e')
	if i == -1:	
		raise Exception("Parse Error: Integer must end with \'e\'")
	num_string = text[1:i]
	for c in num_string:	
		if not is_int(c):
			raise Exception("Parse Error: i must follow with an integer, ended by the character \'e\'")
	return (1 + len(num_string) + 1, int(num_string)) # 'i' + strlen(num_string) + 'e'
		

def load_file(filename):
	torrent = open(filename, "rb")
	torrent_data = torrent.read()
	return torrent_data

def info_hash(filename):
	torrent_data = load_file(filename)
	
	(length, metadata) = bencode_parse(torrent_data)	
	info = bencode_encode(metadata['info'])
	info_hash = hashlib.sha1(info).hexdigest()
	
	return info_hash

def info_hash_binary(filename):
	torrent_data = load_file(filename)
	
	(length, metadata) = bencode_parse(torrent_data)	
	info = bencode_encode(metadata['info'])
	return hashlib.sha1(info)
	

def url_hash(filename):
	torrent_data = load_file(filename)
	
	(length, metadata) = bencode_parse(torrent_data)	
	info = bencode_encode(metadata['info'])
	url_hash = hashlib.sha1(info).digest()
	url_hash = urllib.quote_plus(url_hash)	

	return url_hash

def trackers(metadata):
	metadata = bencode_dict_no_tod(metadata)
	if "announce-list" not in metadata.keys():
		if "announce" not in metadata.keys():
			raise Exception("Error: No trackers found in the .torrent file")
		else:
			return [metadata["announce"]]
	else:
		l = []
		for url_list in metadata["announce-list"]:
			for url in url_list:
				l.append(url)
		return l

def http_trackers(metadata):
	metadata = bencode_dict_no_tod(metadata)
	if "announce-list" not in metadata.keys():
		if "announce" not in metadata.keys():
			raise Exception("Error: No trackers found in the .torrent file")
		else:
			return [metadata["announce"]]
	else:
		a = []
		for url_list in metadata["announce-list"]:
			for url in url_list:
				if url[:4] == 'http':
					a.append(url)
		return a

def udp_trackers(metadata):
	metadata = bencode_dict_no_tod(metadata)
	if "announce-list" not in metadata.keys():
		if "announce" not in metadata.keys():
			raise Exception("Error: No trackers found in the .torrent file")
		else:
			return [metadata["announce"]]
	else:
		a = []
		for url_list in metadata["announce-list"]:
			for url in url_list:
				if url[:3] == 'udp':
					a.append(url)
		return a


if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()
		exit()
	
	argv = sys.argv
	opts, args = getopt.getopt(argv, "n", ["no-pieces"])
	
	show_pieces = 0
	
	if ('no-pieces','') in opts:
		show_pieces = 1
	
	torrent_file = open(args[1], "rb")
	torrent_data = torrent_file.read()

	(length, metadata) = bencode_parse(torrent_data)

	print "SHA1 hash of info: " + info_hash(args[1])	

	track = trackers(metadata)
	print "All Trackers: " + str(track) + "\n"
	track = http_trackers(metadata)
	#print "HTTP Trackers: " + str(track) + "\n"
	track = udp_trackers(metadata)
	#print "UDP Trackers: " + str(track) + "\n"
	
