import sys

def usage():
	print "Usage: bit_client <torrent file>"

def is_int(c):
	o = ord(c)
	return (o >= 48 and o <= 57)

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

def bencode_parse_string(text):
	num_digits = 0

	while is_int(text[num_digits]):	
		num_digits += 1

	length = text[:num_digits]
	content = text[num_digits + 1: num_digits + 1 + int(length)]

	return (num_digits + 1 + int(length), content) # length of string + ':' + string itself
	
def bencode_parse_dict(text):
	if text[0] != 'd':
		raise Exception("Dicts must begin with \'d\'")
	index = 1
	d = {}
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
		d[key] = value	
		
	return (index + 1, d)
	
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
	first_char = torrent.read(1)
	if first_char != "d":
		print "Error: Torrent file should begin with a dictionary..."
		exit()
	
	first_line = torrent.readline()
	print first_line
	
	IFS=':'	
	info={} # Empty dictionary

	# Break this up into functions!!!!!!!!!!!
	
	length_end = first_line.index(IFS)


	# torrent_data = torrent.read()
	# print torrent_data	
	# return torrent_data

if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()
		exit()
	
	argv = sys.argv
	torrent_file = open(argv[1], "rb")
	torrent_data = torrent_file.read()
	# d = bencode_parse_dict(first_line)
	(length, i) = bencode_parse_int("i92834928734987e")
	print i
	
	(length, s) = bencode_parse_string("10:jfjfjfjfjf")
	print s

	(length, l) = bencode_parse_dict(torrent_data)
	print l



	
