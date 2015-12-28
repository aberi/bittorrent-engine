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
		# Torrent initialization
		self.file_name = filename	
		self.torrent = TorrentFile.TorrentFile(self.file_name) 
		self.peer_id = request.generate_peer_id()
		self.info_hash = self.torrent.info_hash 	  # The one that you print for debugging
		self.binary_hash = self.torrent.binary_hash() # The one that you send over connections 

		# Network stuff
		self.no_dns = no_dns
		self.connected = False
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		self.port = BIT_TORRENT_DEFAULT_PORT
		self.hostname = socket.gethostname()
		self.addr = socket.gethostbyname(self.hostname)

		while self.port < 6891:
			try:	
				sock.bind(self.addr, self.port)
			except Exception:
				self.port = self.port + 1
				continue
			break	

		socket.timeout(5.0)

		print self.port	

	def send_tracker_request(self):
		info_hash = urllib.quote_plus(self.info_hash)
		return request.generate_request(self.torrent.trackers, info_hash, "")

	def update_peers(self):
		self.peers = request.tracker_request(self.file_name, self.no_dns)
		self.peers.sort()
		
	def print_peers(self):	
		name = ""
		for peer in self.peers:
			(ip, port) = peer
			if not self.no_dns:	
				try:
					name, aliases, address = socket.gethostbyaddr(ip)
					name = " (" + name + ") "
				except socket.herror or socket.timeout:
					pass
			print ip + ":" + port + name

	def connect_to_peer(self, peer):
		(peer_ip, peer_port) = peer 
		self.sock.connect((peer_ip, int(peer_port)))	
		self.is_connected = True

	def random_connection(self):
		r = int(random.random() * len(self.peers))
		peer = self.peers[r]
		self.connect_to_peer(peer)

		(ip, port) = peer
		print "Connecting to peer at " + ip + ":" + port + '\n'


	def peer_handshake(self):
		if not self.is_connected:
			return ""
		else:
			handshake = chr(19) + "BitTorrent protocol" + (8 * chr(0)) + \
			str(client.torrent.binary_hash().digest()) + client.peer_id

			print "Sending handshake:\n \"" + str(handshake) + "\""
			client.sock.send(handshake)
			resp = client.sock.recv(4096)
			return resp

	def parse_handshake(self, handshake):
		index = 0
		l = ord(handshake[0])
		# print "First byte: " + str(l)
		# print handshake[1:l + 1]
		index = l + 1
		tmp = ""
		for i in range(0, 8):
			tmp += str(ord(handshake[index + i])) + ":"
		# print tmp
		index = index + 8
		peer_hash = handshake[index:index + 20]
		# print "Peer's info hash: \n" +  peer_hash
		index = index + 20
		peer_id = handshake[index:index + 20]
		# print "Peer ID: " + peer_id
	
		return peer_hash, peer_id
	
# TESTING

if __name__ == '__main__':
	client = TorrentClient(sys.argv[1], True)

	client.update_peers()
	client.print_peers()	
	client.random_connection()
	resp = client.peer_handshake()	

	print "\nPeer's response to handshake: "	
	print resp

	print "\nOur hash: \n" + client.torrent.binary_hash().digest() + '\n'
	peer_hash, peer_id = client.parse_handshake(resp)

	print "Peer's hash: "
	print peer_hash

	print "\nOur peer ID:\t" + client.peer_id
	
	print "Peer ID:   \t" + peer_id

