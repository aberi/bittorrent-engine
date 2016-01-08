#!/usr/bin/python
import bencoding
import request
import urllib
import sys
import socket
import struct
import random
import math
import errno

import torrent_file
import Peer

BIT_TORRENT_DEFAULT_PORT = 6881
BUFSIZ = 1 << 10

class TorrentClient:
	def __init__(self, filename, no_dns):
		# Torrent initialization
		self.file_name = filename	
		self.torrent = torrent_file.TorrentFile(self.file_name) 
		self.peer_id = request.generate_peer_id()
		self.info_hash = self.torrent.info_hash 	  # The one that you print for debugging
		self.binary_hash = self.torrent.binary_hash() # The one that you send over connections 
		self.peer = None

		# Network stuff
		self.no_dns = no_dns
		self.hostname = socket.gethostname()
		self.port = BIT_TORRENT_DEFAULT_PORT
		self.addr = socket.gethostbyname(self.hostname)
		self.sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)]	# List of sockets 
																				# that will be used 
	
		self.sock = self.sockets[0]	
		self.current_socket = 0							# Index of the current socket being used
		self.num_connections = 0
	
		self.bitfield = [False] * self.bitfield_length_bytes() * 8

		# Connection information
		self.is_connected = False	# Whether the client is connected to some peer
		self.connected_peers = []	# List of peers the client is currently connected to
		# Connections start with each peer choking the other and not interested in the other
		self.is_choked = True 
		self.is_interested = False 
		self.is_choking = True 
		self.is_interesting = False 

		while self.port < 6891:
			try:	
				self.sock.bind(self.addr, self.port)
			except Exception:
				self.port = self.port + 1
				continue
			break	

		socket.timeout(1.0)

	def close_connection(self):
		self.sock.close()

	def send_tracker_request(self):
		info_hash = urllib.quote_plus(self.info_hash)			# Needs to be sent in this format
		return request.generate_request(self.torrent.trackers, info_hash, self.peer_id, "")
	

	def update_peers(self):
		self.peers = request.tracker_request(self.file_name, self.no_dns)	
		self.peers.sort()

	def switch_sock(self, index):
		if index < 0 or index > len(self.sockets):
			return
		else:
			self.current_socket = index
			self.sock = sockets[index]

		
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

	# Connect to the peer specified by PEER. Should be from the list of peers returned by the tracker
	# for this to work. Only will connect to PEER if the client is not already connected to it.
	def connect_to_peer(self, peer):
		if peer in self.connected_peers:
			return None

		(peer_ip, peer_port) = peer 
		socket.timeout(0.5)
		self.sock.connect((peer_ip, int(peer_port)))	
		self.is_connected = True
		self.peer_ip = peer_ip
		self.peer_port = peer_port
		self.connected_peers.append(peer)
	
		return peer

	# Create a socket specifically for this connection
	def new_connection(self, peer, use_new_connection=True):
		if peer in self.connected_peers:
			return False

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		port = self.port + self.num_connections + 1
		while 1:
			try: 
				s.bind((self.addr, port))
				break
			except socket.error:
				port = port + 1
	
		print "\n\nCreated socket at (" + self.addr + ", " + str(port) + ")"

		(peer_ip, peer_port) = peer
		try:		
			s.settimeout(.5)
			try:
				s.connect((peer_ip, int(peer_port)))
				self.is_connected = True
				print "Current peer is " + peer_ip + ":" + peer_port
				self.peer_ip = peer_ip
				self.peer_port = peer_port
			except socket.timeout:
				return False
		except Exception:
			return False
	
		self.sockets.append(s)
		self.connected_peers.append(peer)

		print "Connected to peer at " + peer_ip + ":" + peer_port + '\n'

		if use_new_connection:
			self.sock = s

		return True					# Was able to connect

	def new_random_connection(self):
		r =	int(random.random() * len(self.peers))
		peer = self.peers[r]
		return self.new_connection(peer, True)
		
	# Connect to a randomly chosen peer from the client's list of peers
	def random_connection(self):
		tries = 10
		while tries > 0:
			try:
				r =	int(random.random() * len(self.peers))
				peer = self.peers[r]
				p = self.connect_to_peer(peer)

				(peer_ip, peer_port) = p

				if p != None:
					print "Connected to peer at " + peer_ip + ":" + peer_port + '\n'

				return (peer_ip, peer_port) # which should be the same as p
			except socket.error:
				tries = tries - 1
				continue
	
		return None	


	# Send the initiating handshake to the peer we are currently connected to. Sending
	# a bitfield is optionally (by default, it should not be sent)
	def peer_handshake(self, send_bitfield=False):
		if not self.is_connected:
			conn = self.random_connection()

		handshake = chr(19) + "BitTorrent protocol" + (8 * chr(0)) + \
		str(self.torrent.binary_hash().digest()) + self.peer_id
		if send_bitfield:
			handshake += self.bitfield_raw_bytes(self.bitfield)

		print "Sending handshake to " + self.peer_ip + ":" + self.peer_port + ":\n \"" + str(handshake) + "\""

		try: 	
			self.sock.send(handshake)
		except:
			if self.sock in self.sockets:
				self.sockets.remove(self.sock)
				self.sock.close()
			return ""

		try:	
			resp = self.sock.recv(BUFSIZ)
		except socket.error:
			return ""

		# Ignore errors that occurs as a result of this. See if we can keep connections alive
		try:
			pass
			#self.send_keepalive()
		except:
			pass
		
		return resp

	# Method for parsing all incoming messages that are not the handshake into
	# their length, ID, and content sections.
	#
	# If the handshake has a standard message appended to the end of it (e.g.
	# a bitfield, a have, etc.) then the handshake parser can pass that portion
	# of the message to this method.
	def parse_message(self, msg):
		msg_len = len(msg)
		index = 0	
	
		if msg_len < 4:
			raise Exception("Didn't receive a message that we can parse")

		# First 4 bytes of the message indicate the length of the content of the message
		content_len = struct.unpack("!I", msg[index:index + 4])[0] - 1 # Discard message id byte
		index = index + 4

		print "Length of content: " + str(content_len)

		# 5th byte indicates the message ID, which specifies how to interpret the message content
		# (if there is any).
		msg_id = ord(msg[index])
		index = index + 1
	
		print "Message ID: " + str(msg_id)

		# The rest of the message is the content of the message
		content = msg[index:] 

		bytes_left = content_len - msg_len + 5	
		while bytes_left > 0:
			try:
				buf = self.sock.recv(bytes_left)
			except:
				return content_len, msg_id, content	
			content = content + buf
			bytes_left = bytes_left - len(buf)

		return content_len, msg_id, content 
	
	# Parse the contents of a message BASED ON the ID
	# of the message.	
	def parse_message_content(self, msg_id, msg_content):
		if msg_id == 0:			# Choke	
			print "Peer has choked client"
			self.is_choking = True

		elif msg_id == 1:		# Unchoke
			print "Peer has unchoked client"
			self.is_choking = False

		elif msg_id == 2:		# Interested
			print "Peer is interested in something"
			self.is_interesting = True

		elif msg_id == 3:		# Not Interested
			print "Peer is not interested in something"
			self.is_interesting = False 

		elif msg_id == 4:		# Have
			pass		

		elif msg_id == 5:		# Bitfield
			self.peer.is_seed = True
			for i in range(0, len(msg_content)):
				current_byte = ord(msg_content[i])
				for j in range(0, 8):
					index = i * 8 + j
					if index < self.bitfield_length_bits():
						current_bit = 1 << (8 - j - 1)					# High bits come first
						has_piece = (current_byte & current_bit) != 0	# AND with the current bit to see if peer has piece
						self.peer.bitfield[index] = has_piece		
						self.peer.is_seed = self.peer.is_seed and has_piece		# Only a seed if it has all the pieces
					elif index < (self.bitfield_length_bytes() * 8):
						self.peer.bitfield[index] = False
					else:
						if self.peer.is_seed:
							print "Peer is a seed indeed"
						return 
						
			if self.peer.is_seed:
				print "Peer is a seed indeed"


	def print_peer_bitfield(self):
		if self.peer != None:
			s = ""
			field = self.peer.bitfield
			for i in range(0, self.bitfield_length_bits()):
				if field[i]:
					s += "1"
				else:
					s += "0"
			print s	

	def bitfield_raw_bytes(self, bitfield):
		length = self.bitfield_length_bytes()
		raw_bytes = ""
		for i in range(0, length):
			current_byte = 0
			for j in range(0, 8):
				current_bit = 1 << (8 - j - 1)
				if (bitfield[(8 * i) + j]):
					current_byte += current_bit
			raw_bytes += chr(current_byte)

		# print "\nRaw byte representation of bitfield: " + raw_bytes	
		return raw_bytes

		
	def parse_handshake(self, handshake):
		handshake_length = len(handshake)

		print "Length of response: " + str(handshake_length)	
	
		index = 0
		l = ord(handshake[0])
		index = l + 1
		tmp = ""

		for i in range(0, 8):
			tmp += str(ord(handshake[index + i])) + ":"

		index = index + 8
		peer_hash = handshake[index:index + 20]

		index = index + 20
		peer_id = handshake[index:index + 20]

		index = index + 20

		self.peer = Peer.Peer(self.peer_ip, self.peer_port, peer_hash, peer_id)
		self.peer.bitfield = [False] * self.bitfield_length_bytes() * 8

		if index < len(handshake):		# Peer may have sent a bitfield!!
			msg_length, msg_id, msg = self.parse_message(handshake[index:])
			self.parse_message_content(msg_id, msg)

		return handshake_length, peer_hash, peer_id


	def bitfield_length_bits(self):
		return self.torrent.pieces() / 20


	def bitfield_length_bytes(self):
		return int(math.ceil(float(self.torrent.pieces()) / 160.0))

	# Attempt to connect to up to 30 peers from the list
	def connect_to_all_peers(self):	
		for i in range(0, 30):
			conn = False 
			if i < len(self.peers):
				conn = self.new_connection(self.peers[i])
	
			if conn and not (conn in self.connected_peers):
				resp = self.peer_handshake(True)
				print "Peer responded with " + resp
				if resp != "":
					msg_len, peer_hash, peer_id = self.parse_handshake(resp)
					self.print_peer_bitfield()
	
			print "List of connected peers: " + str(self.connected_peers)

	def send_message_to_peer(self, msg_id, msg_content):
		if msg_id == 0:
			self.sock.send(4 * chr(0))
			return

		msg_len = int(len(msg_content) + 1)
		tmp = chr(msg_len & (0xff << 24)) + chr(msg_len & (0xff << 16)) + chr(msg_len & (0xff << 8)) + chr(msg_len & (0xff))	# High bits first
		msg = tmp + chr(msg_id) + msg_content		# Message ID + the actual message

		self.sock.send(msg)

	def send_keepalive(self):
		self.send_message_to_peer(0, None)

# TESTING

if __name__ == '__main__':
	client = TorrentClient(sys.argv[1], True)

	msg_len = 68

	client.update_peers()
	client.print_peers()	
	
	# client.random_connection()
	resp = client.peer_handshake(True)	

	print "\nPeer's response to handshake: "	
	print resp

	print "\nLength of bitfield in bytes: " + str(client.bitfield_length_bytes())

	msg_len, peer_hash, peer_id = client.parse_handshake(resp)
	
	print "\nPeer's bitfield: " 	
	client.print_peer_bitfield()
	client.bitfield_raw_bytes(client.peer.bitfield)
	client.bitfield_raw_bytes(client.bitfield)
	
	print "\nOur hash: \n" + client.torrent.binary_hash().digest() + '\n'

	print "Peer's hash: "
	print peer_hash

	print "\nOur peer ID:\t" + client.peer_id

	print "Peer ID:   \t" + peer_id
