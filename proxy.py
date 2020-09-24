from multiprocessing.connection import Client
from threading import Thread
import socket

import parse

class QueueWrapper():
	def __init__(self):
		self.server = []
		self.client = []

class ClientQueueWrapper(Thread):
	def __init__(self):
		super(ClientQueueWrapper, self).__init__()
		self.server = []
		self.client = []

	def run(self):
		self.conn = Client(('127.0.0.1', 6000), authkey=b'super special secret')
		while True:
			if len(self.client) > 0:
				packet = self.client.pop(0)
				self.conn.send({
					"type": "remote",
					"packet": packet
				})
			if len(self.server) > 0:
				packet = self.server.pop(0)
				self.conn.send({
					"type": "local",
					"packet": packet
				})

class RemoteProxy(Thread):
	def __init__(self, remote, queue):
		super(RemoteProxy, self).__init__()
		self.game = None
		self.running = False
		self.remote = remote
		self.queue = queue

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect(remote)

	def run(self):
		try:
			while True:
				data = self.server.recv(4096)
				if data:
					try:		 
						data = parse.parse(data, self.remote, self.queue, False)
						if len(self.queue.client) > 0 and self.running:
							packet = self.queue.client.pop(0)
							#print(f"[!] Client queue packet: {packet}")
							self.game.sendall(packet)
					except Exception as e:
						print(f"[R <- {self.remote[1]}] Exception: {e}")

					if len(data) > 0:
						self.game.sendall(data)
		except (ConnectionResetError, ConnectionAbortedError):
			pass

class LocalProxy(Thread):
	def __init__(self, local, queue):
		super(LocalProxy, self).__init__()
		self.server = None
		self.running = False
		self.local = local
		self.queue = queue

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(local)
		sock.listen(1)

		self.game, addr = sock.accept()

	def run(self):
		try:
			while True:
				data = self.game.recv(4096)
				if data:
					try:
						data = parse.parse(data, self.local, self.queue, True)
						if len(self.queue.server) > 0 and self.running:
							packet = self.queue.server.pop(0)
							#print(f"[!] Server queue packet: {packet}")
							self.server.sendall(packet)
					except Exception as e:
						print(f"[L -> {self.local[1]}] Exception: {e}")

					if len(data) > 0:
						self.server.sendall(data)
		except (ConnectionResetError, ConnectionAbortedError):
			pass

class TCPProxy(Thread):
	def __init__(self, local, remote, queue):
		super(TCPProxy, self).__init__()
		self.local = local
		self.remote = remote
		self.queue = queue
		self.running = False

	def run(self):
		while True:
			print(f"[*] Initializing proxy on {self.local[0]}:{self.local[1]}...")
			self.LocalProxy = LocalProxy(self.local, self.queue)
			self.RemoteProxy = RemoteProxy(self.remote, self.queue)

			self.LocalProxy.server = self.RemoteProxy.server
			self.RemoteProxy.game = self.LocalProxy.game

			self.running = True
			self.LocalProxy.running = True
			self.RemoteProxy.running = True

			self.LocalProxy.start()
			self.RemoteProxy.start() 

			print(f"[*] Proxy on {self.local[0]}:{self.local[1]} established!")
