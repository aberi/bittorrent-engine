import bencoding
import sys
import socket
import random 
import urllib
import hashlib

def send_request(remote_host, remote_port, request_string):	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((socket.gethostbyname(socket.gethostname()), 6881)) 
	remote_addr = socket.gethostbyname(remote_host)
	print remote_addr
	print (remote_addr, remote_port)
	sock.connect((remote_addr, remote_port))
	sock.send(request_string)
	s = sock.recv(4096)

	print s

def generate_peer_id():
	random.seed()
	r = random.random()
	r = str(int(r * (10**10)))
	s = hashlib.sha1(r).digest()
	s = urllib.quote_plus(s)	
	
	return s

def url_encode(s):
	return urllib.quote_plus(s)	

# Tracker should have protcol, host, and port in it
def generate_request(tracker, info_hash, filename):
	tracker_proto, tracker_url = tracker.split("://")
	tracker_host, tracker_end = tracker_url.split(":")
	tracker_port, tracker_path = tracker_end.split("/")
	
	print tracker_proto
	print tracker_host
	print tracker_port

	peer_id = generate_peer_id()

	request = "GET /announce?"
	request = request + "info_hash=" + str(info_hash)
	request = request + "&peer_id=" + peer_id
	request = request + "&port=" + str(6881)
	request = request + "&uploaded=0"
	request = request + "&downloaded=0"
	request = request + "&left=10000"
	request = request + "&compact=1"
	request = request + " HTTP/1.1\r\n\r\n"
	
	print request
	
	send_request(tracker_host, int(tracker_port), request)
	
	

if __name__ == "__main__":
	argv = sys.argv
	
	filename = argv[1]
	
	h = bencoding.url_hash(filename)
	torrent_file = open(filename, "rb")
	torrent_data = torrent_file.read()
	
	(length, metadata) = bencoding.bencode_parse(torrent_data)
	
	track = bencoding.trackers(metadata)
	print track
	generate_request(track[0], h, "")
