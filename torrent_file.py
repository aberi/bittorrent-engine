#!/usr/bin/python

import bencoding
import request
import sys

class TorrentFile:
	def __init__(self, filename):
		self.name = filename 									# name of file
		self.f = open(filename, "rb")							# Actual underlying file object
		self.data = self.f.read()								# Contents of file
		self.info_hash = bencoding.info_hash(filename)			# Hash of the info section of the torrent file
		(self.length, d) = bencoding.bencode_parse(self.data)	# Python object version of torrent file
		self.dictionary = bencoding.bencode_dict_no_tod(d)		# Python object version of torrent file
		self.trackers = bencoding.trackers(self.dictionary) 	# List of trackers

	def parsed_object(self):
		return self.dictionary
	
	def http_trackers(self):
		return bencoding.http_trackers(self.dictionary)
	
	def binary_hash(self):
		return bencoding.info_hash_binary(self.name)			# Needs to be send to trackers and peers to identify
																# a .torrent file
	def file_length(self):
		l = self.dictionary["info"]["length"]
		if self.dictionary["info"]["length"] != None:			# A single file
			return l

	def piece_length(self):
		l = self.dictionary["info"]["piece length"]
		if self.dictionary["info"]["piece length"] != None:			# A single file
			return l

	def pieces(self):
		l = self.dictionary["info"]["pieces"]
		if self.dictionary["info"]["pieces"] != None:			# A single file
			return len(l)


# TESTING	

if __name__ == '__main__':

	filename="ubuntu-gnome-15.10-desktop-amd64.iso.torrent"

	if len(sys.argv) >= 2:
		filename = sys.argv[1]	
	
	t = TorrentFile(filename)

	print t.info_hash
	print t.parsed_object()
	print t.trackers
	print t.http_trackers()
	print t.file_length()
	print t.piece_length()
	print t.pieces()
