import bencoding
import sys

def parse(filename):
	torrent_data = bencoding.load_file(filename)
	
	

if __name__ == "__main__":
	if len(sys.argv) < 2:
		bencoding.usage()
		exit()
	
	argv = sys.argv
	parse(argv[1])
