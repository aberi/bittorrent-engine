import bencoding
import request
import torrent_file
import TorrentClient
import socket
import subprocess

# def test_

def test_client_init(filename):
	client = TorrentClient.TorrentClient(filename, True)

def test_client_tracker_request(filename):
	client = TorrentClient.TorrentClient(filename, True)
	print client.send_tracker_request()

def test_client_update_peers(filename):
	client = TorrentClient.TorrentClient(filename, True)
	client.update_peers()
	print "List of peers (IP:Port) :\n"
	client.print_peers()

def test_random_connection_and_handshake(filename):
	client = TorrentClient.TorrentClient(filename, True)
	client.update_peers()
	response = client.peer_handshake(True)

	return response

def test_new_connection(client):
	for i in range(0, len(client.peers)):
		conn = client.new_random_connection()

		if conn != None and not (conn in client.connected_peers):
			resp = client.peer_handshake(True)
			print "Peer responded with " + resp
			if resp != "":
				msg_len, peer_hash, peer_id = client.parse_handshake(resp)
				client.print_peer_bitfield()

		print "List of connected peers: " + str(client.connected_peers)
	

if __name__ == "__main__":
	subprocess.call("ls")
	filename = raw_input("Enter filename: ")
	# print test_random_connection_and_handshake(filename)

	# New connections	
	
	client = TorrentClient.TorrentClient(filename, True)
	client.update_peers()
	client.connect_to_all_peers()

	print "Attempted to connect with every peer given by the tracker"
