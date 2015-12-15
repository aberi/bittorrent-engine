#!/usr/bin/python

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
	sock.settimeout(5.0)
	print "Sending request to " + str(remote_addr) + " (" + remote_host + ") over port " + str(remote_port) + "\n"
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
def generate_request(trackers, info_hash, filename):
	for i in range(0, len(trackers)):
		tracker = trackers[i]
		tracker_proto, tracker_url = tracker.split("://")
		if ':' in tracker_url:
			tracker_host, tracker_end = tracker_url.split(":")
			tmp = tracker_end.split("/")
			if len(tmp) > 1:
				tracker_port, tracker_path = tmp
			else:
				tracker_port = tmp[0]
		else:
			tracker_port = 80
			tmp = tracker_url.split("/")
			if len(tmp) > 1:
				tracker_host, tracker_path = tmp
			else:
				tracker_host = tmp[0]	

		try:
			socket.gethostbyname(tracker_host)
		except Exception:
			continue

		break
	
		
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

	print "Client Request: \n"	
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
	
	track = bencoding.http_trackers(metadata)
	
	if len(track) == 0:
		raise Exception("No HTTP trackers found (engine does not currently support UDP trackers)")
	
	print "Using tracker at " + track[0]
	# print
	resp = generate_request(track, h, "")
	# print "Tracker Response: \n"
	# print resp
	# print
	
	(x, r) = parse_tracker_response(resp)
	d = bencoding.bencode_dict_no_tod(r)
	
	# print "Python object version of tracker response: \n"
	# print str(d) + '\n'

	peers = ""
	
	try:
		peers = d["peers"]
	except KeyError:
		try:
			tmp = d["peers6"]
		except KeyError:
			raise Exception("Didn't find peers")
		raise Exception("IPv6 not supported!")

	l = [None] * (len(peers) / 6)

	for i in range(0, len(peers) / 6):
		ip = str(ord(peers[i * 6])) + '.' + str(ord(peers[i * 6 + 1])) + '.' + str(ord(peers[i * 6 + 2])) + '.' + str(ord(peers[i * 6 + 3])) 
		port = str(((ord(peers[i * 6 + 4]) << 8) + ord(peers[i * 6 + 5])))
		l[i] = ip + ':' + port
	
	l.sort()	
	print "List of peers (ip:port)"
	for addr in l:
		ip, port = addr.split(":")
		try:
			name, alias, address = socket.gethostbyaddr(ip)
		except Exception:
			pass
		print addr + " (" + name + ") "

