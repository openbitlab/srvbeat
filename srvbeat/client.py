import socket 


def testClient():
	import sys 

	HOST = "127.0.0.1"

	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
		PORT = 65432

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		s.sendall(b"SB|1|bitcoin-node|CPU:50|RAM:55|DISK:23,54,87|gb")
		data = s.recv(1024)

	print(f"Received {data!r}")
	s.close()