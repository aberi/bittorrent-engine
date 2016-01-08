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

	print "\nList of connected peers:"
	for i in range(0, len(client.connected_peers)):
		(ip, port) = client.connected_peers[i]
		print "(" + str(i+1) + ") " + ip + ":" + port	

	print "Number of sockets: " + str(len(client.sockets))
	print "Number of connected peers: " + str(len(client.connected_peers))
	print "Number of peer objects: " + str(len(client.all_connected_peers))
	
	while True:
		entry = int(raw_input("\nEnter peer to receive data from: "))
		entry = entry - 1
		while True:
			msg_len, msg_id, msg = client.receive_message_from_peer(entry)
			client.parse_message_content(msg_id, msg)
			print msg
