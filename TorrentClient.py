#!/usr/bin/python
import bencoding
import request
import urllib
import sys
import socket
import struct
import random

import TorrentFile

BIT_TORRENT_DEFAULT_PORT = 6881

class TorrentClient:
	def __init__(self, filename, no_dns):
		self.no_dns = no_dns
		self.file_name = filename	
		self.torrent = TorrentFile.TorrentFile(self.file_name) 
		self.peer_id = request.generate_peer_id()

	def send_tracker_request(self):
		info_hash = urllib.quote_plus(self.torrent.info_hash)
		return request.generate_request(self.torrent.trackers, info_hash, "")

	def update_peers(self):
		self.peers = request.tracker_request(self.file_name, self.no_dns)
		self.peers.sort()
	
# TESTING

if __name__ == '__main__':
	no_dns = True 
	client = TorrentClient(sys.argv[1], no_dns)

	print client.peer_id
	print client.torrent.http_trackers()

	client.update_peers()
	name = ""
	socket.timeout(5.0)
	
	for peer in client.peers:
		(ip, port) = peer
		if not no_dns:	
			try:
				name, aliases, address = socket.gethostbyaddr(ip)
				name = " (" + name + ") "
			except socket.herror or socket.timeout:
				pass
		print ip + ":" + port + name

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	host_port = BIT_TORRENT_DEFAULT_PORT
	while host_port < 6891:
		try:	
			sock.bind((socket.gethostbyname(socket.gethostname()), host_port))
		except:
			host_port = host_port + 1
			continue
		break	
	
	if host_port >= 6891:
		raise Exception("Couldn't find an available port: Ports 6881-6890 are in use.")

	socket.timeout(5.0)

	r = int(random.random() * len(client.peers))

	(ip, port) = client.peers[r]
	
	sock.connect((ip, int(port)))

	print "Connecting to peer at " + ip + ":" + port
	handshake = "\x19BitTorrent protocol" + (8 * chr(0)) + str(client.torrent.binary_hash().digest()) + client.peer_id
	sock.send(handshake)
	resp = sock.recv(4096)

	print "First byte of the peer response: " + str((struct.unpack("!I", resp[0:4])[0]) >> 24)
	print "Length of response: " + str(len(resp))
	print resp


