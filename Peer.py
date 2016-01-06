#!/usr/bin/python
class Peer:
	def __init__(self, ip, port, info_hash, peer_id):
		self.ip = ip
		self.port = port
		self.info_hash = info_hash
		self.peer_id = peer_id
		self.bitfield = []					# Bitfield optionally sent immediately after the handshake. If it remains
											# the empty list, that means that the bitfield was not sent.
		self.is_seed = False				
