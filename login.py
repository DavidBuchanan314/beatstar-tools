import io
import time
import gzip
import socket
import ssl
import random
import requests
import pprint as pprintlib
pprint = pprintlib.PrettyPrinter(sort_dicts=False).pprint

import raksha
import protos

APP_VERSION = '999.9.9.99999'
DEFAULT_HOSTNAME = "socket-gateway.prod.flamingo.apelabs.net"

ssl_ctx = ssl.create_default_context()

class FlamingoSession():
	def __init__(self, hostname=DEFAULT_HOSTNAME, port=443, use_ssl=True):
		# TODO: use async networking
		sock = socket.create_connection((hostname, port))
		if use_ssl:
			self.sock = ssl_ctx.wrap_socket(sock, server_hostname=hostname)
		else:
			self.sock = sock
		
		self.authenticated = False
		self.resource_urls = None
		self.resource_cache = {}

		self.packet_index = 1
	
	def get_timestamp(self):
		return int(time.time()*1000)

	def generate_rpc_id(self):
		return f"rpc-{self.packet_index}-{random.randint(100000, 999999)}"

	def receive_packet(self, response_proto={}):
		pktlen = int.from_bytes(self.sock.recv(4), "big")
		pkt = self.sock.recv(pktlen)
		headerlen = int.from_bytes(pkt[:4], "big")
		header_bytes = pkt[4:4+headerlen]
		body_bytes = pkt[4+headerlen:]
		header = raksha.parse_proto(io.BytesIO(header_bytes), protos.response_header_proto)
		if header.get("gzipped"):
			body_bytes = gzip.decompress(body_bytes)
		body = raksha.parse_proto(io.BytesIO(body_bytes), response_proto)
		return header, body

	def send_packet(self, header, body, body_proto):
		buf = io.BytesIO()
		raksha.serialize_proto(buf, header, protos.request_header_proto)
		header_len = len(buf.getvalue())
		raksha.serialize_proto(buf, body, body_proto)
		packet_len = len(buf.getvalue()) + 4

		packet = packet_len.to_bytes(4, "big")
		packet += header_len.to_bytes(4, "big")
		packet += buf.getvalue()
		
		self.sock.send(packet)

		self.packet_index += 1

	def login(self, cinta=None):
		rpc_id = self.generate_rpc_id()
		self.send_packet({
			'version': APP_VERSION,
			'service': 'userservice',
			'rpcthing': rpc_id,
			'unk0': 1,
			'unk1': 2
		},{
			'id': 1,
			'type': 7,
			'appVersion': APP_VERSION,
			'timestamp': self.get_timestamp(),
			'all_in_one_login': {
				#'cinta': '676d4d53-f0cb-41c6-8c27-4bb3c3c3c905', # comment out for fresh identity
				'???': 1
			}
		}, protos.userservice_basereq_proto)

		login_res_header, login_res = self.receive_packet(protos.userservice_baseresp_proto)

		#print("login_res_header")
		#pprint(login_res_header)
		#print("login_res")
		#pprint(login_res)

		assert(login_res_header["rpcthing"] == rpc_id)
		assert(login_res["status"] == 200)

		auth_resp = login_res["resp_login_of_some_type"]
		self.authentication_ticket = auth_resp["authenticationTicket"]
		self.clide = auth_resp["clide"]
		self.cinta = auth_resp["cinta"]

		self.authenticated = True
	
	def get_cms_urls(self):
		if not self.authenticated:
			self.login()

		rpc_id = self.generate_rpc_id()
		self.send_packet({
			'version': APP_VERSION,
			'service': 'cmsservice',
			'rpcthing': rpc_id,
			'authenticationTicket': self.authentication_ticket,
			'unk0': 1,
			'unk1': 2,
			'clide': self.clide
		},{
			'id': self.packet_index,
			'version': APP_VERSION,
			'timestamp': self.get_timestamp(),
			'unk1': '',
			'versions': {
				'unk0': 1,
				'unk1': '',
				'unk2': 1,
				'vers': {'versionlist': [
					{'name': 'GameConfig'},
					{'name': 'LangConfig', 'locale': 'en'},
					{'name': 'AssetsPatchConfig'},
					{'name': 'AudioConfig'},
					{'name': 'NewsFeed', 'locale': 'en'},
					{'name': 'ScalingConfig'},
					{'name': 'NotificationConfig'},
					{'name': 'FontFallbackConfig'},
					{'name': 'LiveOpsBundleConfig', 'locale': 'en'},
					{'name': 'LiveOpsDeeplinkRewardConfig'}
				]}
			},
			'authenticationTicket': self.authentication_ticket
		}, protos.cmsreq_proto)

		cms_res_header, cms_res = self.receive_packet(protos.cms_res_proto)

		assert(cms_res_header["rpcthing"] == rpc_id)

		#pprint(cms_res_header)
		#pprint(cms_res)

		resources = {}
		for resource in cms_res["blah"]["blah"]["blah"]: # I am good at naming things
			resources[resource["name"]] = {
				"url": resource["url"],
				"hash": resource["hash"],
				"version": resource["version"]
			}
		
		self.resource_urls = resources
		self.resource_cache = {} # TODO: selectively invalidate cache based on versions

		return resources
	
	def get_resource(self, name):
		if not self.resource_urls:
			self.get_cms_urls()
		
		if name in self.resource_cache:
			return self.resource_cache["name"][1]

		url = self.resource_urls[name]["url"]
		version = self.resource_urls[name]["version"]

		resource = gzip.decompress(requests.get(url).content)

		self.resource_cache[name] = (version, resource)

		return resource, version


if __name__ == "__main__":
	session = FlamingoSession()
	session.login()
	pprint(session.get_cms_urls())
