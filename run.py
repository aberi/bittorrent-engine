#!/usr/bin/python
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

# Allow us to evoke the main method in other modules
def main():
	subprocess.call("ls")
	filename = raw_input("Enter filename: ")
	# print test_random_connection_and_handshake(filename)

	# New connections	
	
	client = TorrentClient.TorrentClient(filename, True)
	client.update_peers()
	client.connect_to_all_peers()

	print "\nList of connected peers:"

	i = 0
	for (ip, port) in client.connected_peers:
		print "(" + str(i+1) + ") " + ip + ":" + port
		i = i + 2

	print "Number of sockets: " + str(len(client.sockets))
	print "Number of connected peers: " + str(len(client.connected_peers))
	print "Number of peer objects: " + str(len(client.all_connected_peers))

	while True:
		print "\nList of peers and their message histories..."
		for i in range(0, len(client.all_connected_peers)):
			peer = client.all_connected_peers[i]
			print "Total bytes received from " + peer.ip + ":" + peer.port
			print "All bytes received from peer " + peer.ip + ":" + peer.port + ": "
			print peer.message_history	
			if peer.is_seed:
				print peer.ip + ":" + peer.port + " is a seed"
		try:	

			while True:
				decision = raw_input("Send message to all peers? (y/n)")

				if decision != 'y' and decision != 'n':
					print "Enter \'y\' or \'n\'"
					continue

				all_or_none = decision == 'y'

				choice = int(raw_input("\n0 for receiving data, 1 for keep-alive, \
2 for choke, 3 for unchoke, 4 for interested, 5 for not interested, 6 for have, 7 for request, \
8 to view the status of all connections, 9 to exit\n"))
				
				if choice == 0:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							try:
								while True:
									msg_len, msg_id, msg = client.receive_message_from_peer(entry)
									client.parse_message_content(msg_id, msg)
							except:
								continue
					else:
						entry = int(raw_input("\nEnter peer to receive data from: ")) - 1
						while True:
							msg_len, msg_id, msg = client.receive_message_from_peer(entry)
							client.parse_message_content(msg_id, msg)
	
				elif choice == 1:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):	
							client.send_keepalive(entry)	
					else:
						entry = int(raw_input("\nEnter peer to send keep-alive to: ")) - 1
						client.send_keepalive(entry)	

				elif choice == 2:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							client.send_choke(entry)	
					else:
						entry = int(raw_input("\nEnter peer to choke: ")) - 1
						client.send_choke(entry)	

				elif choice == 3:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							client.send_unchoke(entry)	
					else:
						entry = int(raw_input("\nEnter peer to unchoke: ")) - 1
						client.send_unchoke(entry)	

				elif choice == 4:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							client.send_interested(entry)	
					else:
						entry = int(raw_input("\nEnter peer to be interested in: ")) - 1
						client.send_interested(entry)	

				elif choice == 5:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							client.send_not_interested(entry)	
	
					else:
						entry = int(raw_input("\nEnter peer to be uninterested in: ")) - 1
						client.send_not_interested(entry)	

				elif choice == 6:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):
							piece = int(raw_input("Enter the index of the piece that you have: "))
		
							msg = chr(0) + chr(0) + chr(0) + chr(5) + chr(4) + piece
							client.send_message_to_peer(4, msg, entry)
					else:	
						entry = int(raw_input("\nEnter peer to send the have to:")) - 1
						piece = int(raw_input("Enter the index of the piece that you have: "))
	
						msg = chr(0) + chr(0) + chr(0) + chr(5) + chr(4) + piece
						client.send_message_to_peer(4, msg, entry)
	
				elif choice == 7:
					if all_or_none:
						for entry in range(0, len(client.all_connected_peers)):	
							client.send_request(piece, 1 << 14, 0, entry)

					else:	
						entry = int(raw_input("\nEnter peer to send request to: ")) - 1
						piece = int(raw_input("Enter the index of the piece that you want"))
		
						client.send_request(piece, 1 << 14, 0, entry)
		
				elif choice == 8:
					for p in range(0, len(client.all_connected_peers)):
						client.all_connected_peers[p].print_connection_status()
						
				elif choice == 9:
					exit()
		except:
			if choice == 9:
				exit()

		i = 0
		for (ip, port) in client.connected_peers:
			print "(" + str(i + 1) + ") " + ip + ":" + port
			i = i + 1
					

if __name__ == "__main__":
	main()
