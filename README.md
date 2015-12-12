# bittorrent-engine
BitTorrent engine client. This can be used as a backend for many P2P projects!

To see the BEncoding parser, do

    python bencoding.py <torrent file>

and the file will be loaded into Python as a dictionary (per the BitTorrent protocol. All .torrent files should be a 
BEncoded dictionary.

For example,

    python bencoding.py kali-linux-light-2.0-amd64.torrent

gives

    {'comment': 'kali-linux-light-2.0-amd64', 'info': {'files': [{'path': ['kali-linux-light-2.0-amd64.iso'], 
	 'length': 906461184}, {'path': ['kali-linux-light-2.0-amd64.txt.sha1sum'], 'length': 74}], 
	 'piece length': 262144, 'name': 'kali-linux-light-2.0-amd64'}, 
	 'creation date': 1439301669, 'announce-list': [['http://tracker.kali.org:6969/announce'], 
     ['udp://tracker.kali.org:6969/announce']], 
	 'created by': 'ruTorrent (PHP Class - Adrien Gibrat)', 
	 'announce': 'http://tracker.kali.org:6969/announce'} 

I chose to leave out the pieces from this object because they're a bunch of SHA1 output that clogs the screen.
 
