from multiprocessing.connection import Listener
from importlib import reload
from threading import Thread
import socket
import time
import os

import fridahook
import proxy
import parse

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

class ListenerThread(Thread):
	def __init__(self, queue):
		super(ListenerThread, self).__init__()
		self.queue = queue

		self.listener = Listener(('0.0.0.0', 6000), authkey=b'super special secret')

	def run(self):
		try:
			while True:
				self.conn = self.listener.accept()
				payload = self.conn.recv()

				if payload["type"] == "remote":
					self.queue.client.append(payload["packet"])
				if payload["type"] == "local":
					self.queue.server.append(payload["packet"])
		except:
			pass

if __name__ == "__main__":
	print("---- PwnAdventure3 Game Hack ----\n")
	print("-- PwnAdventure3 TCP Proxy --\n")

	canProxy = True
	queue = None

	try:
		listener = ListenerThread(queue)
		listener.start()
		queue = proxy.QueueWrapper()
	except:
		print("[!] A TCP proxy is already active, proxying is disabled.")
		queue = proxy.ClientQueueWrapper()
		queue.start()
		canProxy = False
		
	if canProxy:
		time.sleep(0.5)
		master = proxy.TCPProxy(('0.0.0.0', 3333), ('server.brycec.me', 3333), queue)
		master.start()

		proxies = []
		for port in range(4700, 4705 + 1):
			time.sleep(0.5)

			p = proxy.TCPProxy(('0.0.0.0', port), ('server.brycec.me', port), queue)
			p.start()
			proxies.append(p)

	hook = fridahook.FridaHook()

	utils = parse.Utils(queue, parse, hook)
	hook.utils = utils

	while True:
		try:
			cmd = input('')
			if cmd == 'quit' or cmd == 'q':
				os._exit(0)
			if not parse.cmd_parse(cmd, hook):	
				reload(parse)
				utils = parse.Utils(queue, parse, hook)

				hook.unload()
				reload(fridahook)
				hook = fridahook.FridaHook()
				hook.utils = utils
		except Exception as e:
			print(e)
