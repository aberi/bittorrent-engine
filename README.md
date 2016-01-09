# bittorrent-engine
BitTorrent engine client. This can be used as a backend for many P2P projects!

So far, the client can only 

	- Parse bencoding (i.e. .torrent files)

	- Send requests to HTTP trackers

	- Connect to peers and send handshakes

	- Receive bitfields from peers and save them

	- Receive and parse a limited number of BitTorrent peer wire messages (keep-alive, choke, unchoke, interested, not interested, bitfield)
