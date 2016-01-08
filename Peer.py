#!/usr/bin/python
class Peer:
	def __init__(self, ip, port, socket=None):
		self.ip = ip
		self.port = port
		self.bitfield = []					# Bitfield optionally sent immediately after the handshake. If it remains
											# the empty list, that means that the bitfield was not sent.
		self.is_seed = False				

		self.message_history = ""
