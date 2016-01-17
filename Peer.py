#!/usr/bin/python
class Peer:
	def __init__(self, ip, port, socket=None):
		self.ip = ip
		self.port = port
		self.bitfield = []					# Bitfield optionally sent immediately after the handshake. If it remains
											# the empty list, that means that the bitfield was not sent.
		self.is_seed = False				

		self.message_history = ""

		# Start with the default bits. Adjust according to the messages received!!!

		self.is_choked = True 
		self.is_choking = True 
		self.is_interested = False
		self.is_interesting = False

	def addr(self):
		return self.ip + ":" + self.port
	
	def print_connection_status(self):
		print "Status of connection with " + self.addr() + "\n"
	
		print "Is choked: " + str(self.is_choked)	
		print "Is choking: " + str(self.is_choking)	
		print "Is interested: " + str(self.is_interested)	
		print "Is interesting: " + str(self.is_interesting)	+ "\n"


	
