import bencoding
import sys
import socket
import random 
import urllib
import hashlib

BUFSIZ = 4096

def send_request(remote_host, remote_port, request_string):	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((socket.gethostbyname(socket.gethostname()), 6881)) 
	remote_addr = socket.gethostbyname(remote_host)
	sock.connect((remote_addr, remote_port))
	sock.send(request_string)

	resp = ""
	s = sock.recv(BUFSIZ)
	while s != "":
		resp = resp + s
		s = sock.recv(BUFSIZ)
	
	return resp 

def parse_tracker_response(resp):
	p = resp
	i = resp.index("\r\n")
	while i != -1: #and p[:2] != "\r\n":
		p = p[i+ 2:]
		try:
			i = p.index("\r\n")
		except ValueError:
			break	
	b = bencoding.bencode_parse_dict(p)
	return b

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

	print "Client Request:"	
	print request
	print 	
	return send_request(tracker_host, int(tracker_port), request)
	
	

if __name__ == "__main__":
	argv = sys.argv
	
	filename = argv[1]
	
	h = bencoding.url_hash(filename)
	torrent_file = open(filename, "rb")
	torrent_data = torrent_file.read()
	
	(length, metadata) = bencoding.bencode_parse(torrent_data)
	
	track = bencoding.trackers(metadata)
	
	print "Using tracker at " + track[0]
	print
	resp = generate_request(track[0], h, "")
	print "Tracker Response: "
	print resp
	print
	
	(x, r) = parse_tracker_response(resp)
	d = bencoding.bencode_dict_no_tod(r)

	peers = d["peers"]

	l = [None] * (len(peers) / 6)

	for i in range(0, len(peers) / 6):
		s = str(ord(peers[i * 6])) + '.' + str(ord(peers[i * 6 + 1])) + '.' + str(ord(peers[i * 6 + 2])) + '.' + str(ord(peers[i * 6 + 3])) + ':'  \
		+ str(((ord(peers[i * 6 + 4]) << 8) + ord(peers[i * 6 + 5])))
		l[i] = s
	
	l.sort()	
	print "List of peers (ip:port)"
	for ip in l:
		print ip

